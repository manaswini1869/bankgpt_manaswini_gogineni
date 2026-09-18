import argparse
import asyncio
import json
from urllib.parse import urlparse

from app.agent.loop import DiscoveryAgent
from app.agent.planner import OpenAIPlanner
from app.artifact.schema import CapabilityArtifact
from app.artifact.store import ArtifactStore
from app.config import get_settings


def _parse_parameter(value: str, default_type: str):
    name, separator, description = value.partition("=")
    parameter_name, type_separator, parameter_type = name.partition(":")
    if not type_separator:
        parameter_type = default_type
    if not parameter_name or not separator or not description:
        raise argparse.ArgumentTypeError("parameters must use name[:type]=description")
    return parameter_name, {"type": parameter_type, "description": description}


def _parse_marker(value: str):
    marker, separator, message = value.partition("=")
    if not marker or not separator or not message:
        raise argparse.ArgumentTypeError("markers must use text=message")
    return marker, message


def build_artifact(steps, *, args):
    host = urlparse(args.entrypoint).hostname
    inputs = dict(_parse_parameter(value, "string") for value in args.input)
    outputs = dict(_parse_parameter(value, "string") for value in args.output)
    input_names = list(inputs)
    fill_index = 0
    for step in steps:
        if step.action.value == "fill" and fill_index < len(input_names):
            step.value = "{{" + input_names[fill_index] + "}}"
            fill_index += 1
    for step in steps:
        if step.output:
            outputs.setdefault(step.output, {"type": "string", "description": f"Extracted value: {step.output}"})
    return CapabilityArtifact.model_validate({
        "schema_version": "1.0",
        "id": args.capability_id,
        "version": 1,
        "name": args.name,
        "description": args.description,
        "target_app": args.target_app,
        "entrypoint": args.entrypoint,
        "inputs": inputs,
        "outputs": outputs,
        "steps": steps,
        "checkpoint": {"strategy": args.checkpoint_strategy, "expected": args.checkpoint},
        "policy": {
            "allowed_actions": ["navigate", "fill", "click", "extract", "wait"],
            "allowed_domains": [args.allowed_domain or host],
            "risk": "read_only",
        },
        "outcome_markers": {
            "business": dict(args.business_marker),
            "recoverable": dict(args.recoverable_marker),
        },
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("goal")
    parser.add_argument("--entrypoint", default=get_settings().demo_base_url)
    parser.add_argument("--capability-id", default="bank_workflow")
    parser.add_argument("--name", default="Bank workflow")
    parser.add_argument("--description", default="A discovered workflow for a bank web application.")
    parser.add_argument("--target-app", default="bank-web-app")
    parser.add_argument("--input", action="append", default=[], help="name[:type]=description")
    parser.add_argument("--output", action="append", default=[], help="name[:type]=description")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-strategy", choices=["text", "locator", "url"], default="text")
    parser.add_argument("--allowed-domain")
    parser.add_argument("--business-marker", action="append", type=_parse_marker, default=[])
    parser.add_argument("--recoverable-marker", action="append", type=_parse_marker, default=[])
    args = parser.parse_args()
    settings = get_settings()
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for discovery. Copy .env.example to .env and set it.")
    planner = OpenAIPlanner(settings.openai_api_key, settings.openai_model)
    agent = DiscoveryAgent(planner, settings.evidence_dir, headless=settings.headless, max_steps=settings.agent_max_steps)
    artifact, logger = asyncio.run(
        agent.run(args.goal, args.entrypoint, lambda steps: build_artifact(steps, args=args))
    )
    if artifact:
        path = ArtifactStore(settings.artifact_dir).save(artifact)
        print(json.dumps({"artifact": str(path), "evidence": str(logger.path)}, indent=2))
    else:
        print(json.dumps({"status": "escalated", "evidence": str(logger.path)}, indent=2))


if __name__ == "__main__":
    main()
