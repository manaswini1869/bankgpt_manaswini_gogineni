import json
from pathlib import Path

from app.artifact.schema import CapabilityArtifact
from app.generator.playwright import PlaywrightCodeGenerator


def test_generator_emits_playwright():
    artifact = CapabilityArtifact.model_validate(json.loads(Path("artifacts/lookup_member_balance.v1.json").read_text()))
    code = PlaywrightCodeGenerator().generate(artifact)
    assert "get_by_label('Member ID')" in code
    assert "get_by_role('button', name='Search')" in code
    assert "get_by_label('Savings Balance')" in code
