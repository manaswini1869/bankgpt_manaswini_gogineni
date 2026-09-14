import argparse
import asyncio
import json

from app.agent.loop import DiscoveryAgent
from app.agent.planner import OpenAIPlanner
from app.artifact.schema import CapabilityArtifact
from app.artifact.store import ArtifactStore
from app.config import get_settings


def build_artifact(steps):
    return CapabilityArtifact.model_validate({
        "schema_version": "1.0",
        "id": "lookup_member_balance",
        "version": 1,
        "name": "Look up member balance",
        "description": "Look up a member and return their savings balance.",
        "target_app": "bank-demo",
        "entrypoint": get_settings().demo_base_url,
        "inputs": {"member_id": {"type": "string", "description": "Bank member identifier"}},
        "outputs": {"savings_balance": {"type": "number", "description": "Current savings balance"}},
        "steps": steps,
        "checkpoint": {"strategy": "text", "expected": "Member Details"},
        "policy": {
            "allowed_actions": ["navigate", "fill", "click", "extract", "wait"],
            "allowed_domains": ["127.0.0.1", "localhost"],
            "risk": "read_only",
        },
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("goal", nargs="?", default="Look up member 12345 and return their savings balance")
    args = parser.parse_args()
    settings = get_settings()
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for discovery. Copy .env.example to .env and set it.")
    planner = OpenAIPlanner(settings.openai_api_key, settings.openai_model)
    agent = DiscoveryAgent(planner, settings.evidence_dir, headless=settings.headless, max_steps=settings.agent_max_steps)
    artifact, logger = asyncio.run(agent.run(args.goal, settings.demo_base_url, build_artifact))
    if artifact:
        path = ArtifactStore(settings.artifact_dir).save(artifact)
        print(json.dumps({"artifact": str(path), "evidence": str(logger.path)}, indent=2))
    else:
        print(json.dumps({"status": "escalated", "evidence": str(logger.path)}, indent=2))
