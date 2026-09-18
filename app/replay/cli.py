import argparse
import asyncio
import json

from app.artifact.store import ArtifactStore
from app.config import get_settings
from app.replay.engine import ReplayEngine


def _parse_input(value: str):
    name, separator, input_value = value.partition("=")
    if not name or not separator:
        raise argparse.ArgumentTypeError("inputs must use name=value")
    return name, input_value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", default="artifacts/lookup_member_balance.v1.json")
    parser.add_argument("--input", action="append", type=_parse_input, default=[])
    parser.add_argument("--member-id", help="Compatibility alias for the demo artifact")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    store = ArtifactStore(settings.artifact_dir)
    from app.artifact.schema import CapabilityArtifact
    path = args.artifact
    artifact_obj = CapabilityArtifact.model_validate(json.loads(open(path).read()))
    inputs = dict(args.input)
    if args.member_id is not None:
        inputs["member_id"] = args.member_id
    engine = ReplayEngine(store, settings.evidence_dir, headless=not args.headed)
    result = asyncio.run(engine.run(artifact_obj, inputs))
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    raise SystemExit(0 if result.status.value in {"success", "business_outcome", "recoverable", "escalated"} else 1)


if __name__ == "__main__":
    main()
