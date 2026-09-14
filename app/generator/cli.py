import argparse
import json

from app.artifact.schema import CapabilityArtifact
from app.config import get_settings
from app.generator.playwright import PlaywrightCodeGenerator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", default="artifacts/lookup_member_balance.v1.json")
    args = parser.parse_args()
    settings = get_settings()
    artifact = CapabilityArtifact.model_validate(json.loads(open(args.artifact).read()))
    path = PlaywrightCodeGenerator().write(artifact, settings.generated_dir)
    print(path)
