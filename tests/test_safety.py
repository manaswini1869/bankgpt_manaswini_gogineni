import json
from pathlib import Path

import pytest

from app.artifact.schema import CapabilityArtifact, ActionType
from app.safety.policy import PolicyViolation, SafetyPolicy


def artifact():
    return CapabilityArtifact.model_validate(json.loads(Path("artifacts/lookup_member_balance.v1.json").read_text()))


def test_allowlisted_action():
    SafetyPolicy().check_action(ActionType.CLICK, artifact())


def test_block_non_allowlisted_action():
    a = artifact()
    a.policy.allowed_actions = [ActionType.EXTRACT]
    with pytest.raises(PolicyViolation):
        SafetyPolicy().check_action(ActionType.CLICK, a)
