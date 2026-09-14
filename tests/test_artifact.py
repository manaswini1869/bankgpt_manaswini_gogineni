import json
from pathlib import Path

from app.artifact.schema import CapabilityArtifact


def test_example_artifact_is_valid():
    path = Path("artifacts/lookup_member_balance.v1.json")
    artifact = CapabilityArtifact.model_validate(json.loads(path.read_text()))
    assert artifact.id == "lookup_member_balance"
    assert artifact.inputs["member_id"].type.value == "string"
    assert artifact.outputs["savings_balance"].type.value == "number"
