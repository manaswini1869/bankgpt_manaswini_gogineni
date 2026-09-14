from uuid import uuid4

from app.agent.models import AgentDecision
from app.artifact.schema import ActionType, CapabilityArtifact, Step
from app.evidence.logger import EvidenceLogger
from app.safety.policy import SafetyPolicy
from app.surface.playwright import PlaywrightSurface


class DiscoveryRecorder:
    def __init__(self, goal, evidence_root):
        self.goal = goal
        self.logger = EvidenceLogger(evidence_root, "discovery")
        self.steps: list[Step] = []

    def record(self, decision: AgentDecision, target=None):
        action = decision.action.action
        if action in {"finish", "escalate"}:
            return
        locator = None
        if action in {"click", "fill"}:
            from app.artifact.schema import Locator, Target
            locator = Target(locator=Locator(
                strategy=decision.action.strategy or "text",
                value=decision.action.target or decision.action.value or "",
                name=decision.action.name,
                rationale="Selected by discovery agent from observed UI semantics.",
            ))
        step = Step(
            id=f"step_{len(self.steps)+1}",
            action=ActionType(action),
            target=locator,
            value=decision.action.value if action == "fill" else None,
        )
        self.steps.append(step)
        self.logger.event("action_recorded", action=decision.model_dump(mode="json"))


class DiscoveryAgent:
    def __init__(self, planner, evidence_root, headless=False, max_steps=10):
        self.planner = planner
        self.evidence_root = evidence_root
        self.headless = headless
        self.max_steps = max_steps
        self.policy = SafetyPolicy()

    async def run(self, goal: str, entrypoint: str, artifact_builder):
        recorder = DiscoveryRecorder(goal, self.evidence_root)
        surface = PlaywrightSurface()
        await surface.start(entrypoint, headless=self.headless)
        try:
            for _ in range(self.max_steps):
                observation = await surface.observe()
                recorder.logger.event("observation", observation=observation)
                decision = await self.planner.decide(goal, observation)
                recorder.logger.event("decision", decision=decision.model_dump(mode="json"))
                if decision.goal_complete or decision.action.action == "finish":
                    artifact = artifact_builder(recorder.steps)
                    recorder.logger.save_json("artifact.json", artifact.model_dump(mode="json"))
                    return artifact, recorder.logger
                if decision.action.action == "escalate":
                    return None, recorder.logger
                self._check_decision(decision)
                await self._execute(surface, decision)
                recorder.record(decision)
            raise RuntimeError("Discovery max steps exceeded")
        finally:
            await surface.close()

    def _check_decision(self, decision):
        if decision.action.action not in {"navigate", "click", "fill", "wait"}:
            raise ValueError(f"Unsupported discovery action: {decision.action.action}")

    async def _execute(self, surface, decision):
        a = decision.action
        if a.action == "navigate":
            await surface.navigate(a.value)
        elif a.action == "click":
            from app.artifact.schema import Locator
            await surface.click(Locator(strategy=a.strategy, value=a.target or "", name=a.name), 5000)
        elif a.action == "fill":
            from app.artifact.schema import Locator
            await surface.fill(Locator(strategy=a.strategy, value=a.target or "", name=a.name), a.value or "", 5000)
        elif a.action == "wait":
            await surface.wait(int(a.value or 500))
