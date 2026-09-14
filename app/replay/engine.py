import re
import time
from typing import Any
from uuid import uuid4

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.artifact.schema import ActionType, CapabilityArtifact, RunResult, RunStatus
from app.artifact.store import ArtifactStore
from app.evidence.logger import EvidenceLogger
from app.replay.errors import MemberNotFound, RecoverableReplayError
from app.safety.policy import SafetyPolicy
from app.surface.playwright import PlaywrightSurface


_PLACEHOLDER = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")


def render(value: str | None, inputs: dict[str, Any]) -> str | None:
    if value is None:
        return None
    def repl(match):
        key = match.group(1)
        if key not in inputs:
            raise ValueError(f"Missing required input: {key}")
        return str(inputs[key])
    return _PLACEHOLDER.sub(repl, value)


class ReplayEngine:
    def __init__(self, artifact_store: ArtifactStore, evidence_root, headless: bool = True):
        self.artifact_store = artifact_store
        self.evidence_root = evidence_root
        self.headless = headless
        self.policy = SafetyPolicy()

    async def run(self, artifact: CapabilityArtifact, inputs: dict[str, Any], run_id: str | None = None) -> RunResult:
        run_id = run_id or str(uuid4())
        logger = EvidenceLogger(self.evidence_root, "replay", run_id)
        logger.save_json("artifact.json", artifact.model_dump(mode="json"))
        logger.event("replay_started", capability_id=artifact.id, version=artifact.version, inputs=inputs)

        self.policy.validate_artifact(artifact)
        self._validate_inputs(artifact, inputs)

        surface = PlaywrightSurface()
        outputs: dict[str, Any] = {}
        start = time.monotonic()
        try:
            await surface.start(artifact.entrypoint, headless=self.headless)
            for index, step in enumerate(artifact.steps):
                if time.monotonic() - start > 60:
                    raise RecoverableReplayError("Replay timeout exceeded")
                logger.event("step_started", index=index, step_id=step.id, action=step.action.value)
                for attempt in range(step.retry_count + 1):
                    try:
                        self.policy.check_action(step.action, artifact)
                        await self._execute_step(surface, artifact, step, inputs, outputs)
                        break
                    except PlaywrightTimeoutError as exc:
                        logger.event("step_retry", step_id=step.id, attempt=attempt, error=str(exc))
                        if attempt == step.retry_count:
                            raise
                logger.event("step_succeeded", step_id=step.id, outputs=outputs)

            await self._verify_checkpoint(surface, artifact)
            logger.event("replay_succeeded", outputs=outputs)
            return RunResult(
                status=RunStatus.SUCCESS,
                capability_id=artifact.id,
                capability_version=artifact.version,
                outputs=outputs,
                evidence_path=str(logger.path),
                run_id=run_id,
            )
        except MemberNotFound as exc:
            await self._capture_failure(surface, logger, "member_not_found")
            return RunResult(
                status=RunStatus.BUSINESS_OUTCOME,
                capability_id=artifact.id,
                capability_version=artifact.version,
                error_code=exc.code,
                message=str(exc),
                evidence_path=str(logger.path),
                run_id=run_id,
            )
        except RecoverableReplayError as exc:
            await self._capture_failure(surface, logger, "recoverable")
            return RunResult(
                status=RunStatus.RECOVERABLE,
                capability_id=artifact.id,
                capability_version=artifact.version,
                error_code=exc.code,
                message=str(exc),
                evidence_path=str(logger.path),
                run_id=run_id,
            )
        except Exception as exc:
            await self._capture_failure(surface, logger, "failure")
            step_id = None
            try:
                step_id = step.id
            except UnboundLocalError:
                pass
            logger.event("replay_failed", step_id=step_id, error=str(exc))
            return RunResult(
                status=RunStatus.FAILED,
                capability_id=artifact.id,
                capability_version=artifact.version,
                step_id=step_id,
                error_code="HARD_FAILURE",
                message=str(exc),
                evidence_path=str(logger.path),
                run_id=run_id,
            )
        finally:
            await surface.close()

    async def _execute_step(self, surface, artifact, step, inputs, outputs):
        if step.action == ActionType.NAVIGATE:
            url = render(step.value, inputs)
            self.policy.check_navigation(url, artifact)
            await surface.navigate(url)
        elif step.action == ActionType.CLICK:
            await surface.click(step.target.locator, step.timeout_ms)
        elif step.action == ActionType.FILL:
            await surface.fill(step.target.locator, render(step.value, inputs), step.timeout_ms)
        elif step.action == ActionType.EXTRACT:
            value = await surface.extract(step.target.locator, step.timeout_ms)
            outputs[step.output] = self._coerce_output(value, artifact.outputs[step.output].type.value)
        elif step.action == ActionType.WAIT:
            await surface.wait(int(render(step.value, inputs) or 0))

        body = (await surface.observe())["text"]
        if "Member not found" in body:
            raise MemberNotFound("No member matched the supplied member ID")
        if "Temporary application error" in body:
            raise RecoverableReplayError("Temporary application error")

    async def _verify_checkpoint(self, surface, artifact):
        checkpoint = artifact.checkpoint
        if checkpoint.strategy == "text":
            body = (await surface.observe())["text"]
            if checkpoint.expected not in body:
                raise AssertionError(f"Checkpoint text {checkpoint.expected!r} not found")
        elif checkpoint.strategy == "url":
            if checkpoint.expected not in surface.page.url:
                raise AssertionError(f"Checkpoint URL {checkpoint.expected!r} not reached")
        elif checkpoint.strategy == "locator":
            locator = surface.page.get_by_text(checkpoint.expected)
            await locator.wait_for(state="visible")

    def _validate_inputs(self, artifact, inputs):
        required = {name for name, param in artifact.inputs.items() if param.required and param.default is None}
        missing = required - set(inputs)
        if missing:
            raise ValueError(f"Missing required inputs: {sorted(missing)}")

    @staticmethod
    def _coerce_output(value: str, type_name: str):
        if type_name == "number":
            return float(value.replace("$", "").replace(",", ""))
        if type_name == "integer":
            return int(value)
        if type_name == "boolean":
            return value.lower() in {"true", "yes", "1"}
        return value

    async def _capture_failure(self, surface, logger, suffix):
        try:
            await surface.screenshot(str(logger.path / f"{suffix}.png"))
        except Exception:
            pass
