import argparse
import asyncio
import json

from app.artifact.store import ArtifactStore
from app.config import get_settings
from app.replay.engine import ReplayEngine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", default="artifacts/lookup_member_balance.v1.json")
    parser.add_argument("--member-id", default="12345")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    store = ArtifactStore(settings.artifact_dir)
    import json as _json
    from app.artifact.schema import CapabilityArtifact
    path = args.artifact
    artifact_obj = CapabilityArtifact.model_validate(_json.loads(open(path).read()))
    engine = ReplayEngine(store, settings.evidence_dir, headless=not args.headed)
    result = asyncio.run(engine.run(artifact_obj, {"member_id": args.member_id}))
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    raise SystemExit(0 if result.status.value in {"success", "business_outcome", "recoverable", "escalated"} else 1)
