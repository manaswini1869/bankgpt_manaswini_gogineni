from urllib.parse import urlparse

from app.artifact.schema import ActionType, CapabilityArtifact, RiskLevel


class PolicyViolation(Exception):
    pass


class SafetyPolicy:
    def validate_artifact(self, artifact: CapabilityArtifact) -> None:
        for step in artifact.steps:
            if step.action not in artifact.policy.allowed_actions:
                raise PolicyViolation(f"Action {step.action.value} is not allowed")
        host = urlparse(artifact.entrypoint).hostname
        if not host or host not in artifact.policy.allowed_domains:
            raise PolicyViolation(f"Entrypoint host {host!r} is not allowlisted")
        if artifact.policy.risk == RiskLevel.RISKY:
            raise PolicyViolation("Risky capabilities require human approval in this demo")

    def check_navigation(self, url: str, artifact: CapabilityArtifact) -> None:
        host = urlparse(url).hostname
        if host not in artifact.policy.allowed_domains:
            raise PolicyViolation(f"Navigation to host {host!r} is blocked")

    def check_action(self, action: ActionType, artifact: CapabilityArtifact) -> None:
        if action not in artifact.policy.allowed_actions:
            raise PolicyViolation(f"Action {action.value} is blocked by policy")
