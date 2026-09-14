# Computer-Use Automation System

A small implementation of the interface.ai take-home: an LLM discovers a UI workflow once, the workflow becomes a typed capability artifact, and production invocations replay the artifact deterministically without LLM decisions.

## Architecture

```text
Goal -> Discovery Agent -> Capability Artifact -> Deterministic Replay
                                      |                 |
                                      |                 +-> RunResult / evidence
                                      +-> Capability API
                                      +-> Playwright code generator
```

The artifact is the single source of truth for replay, the capability catalog, and code generation.

## Prerequisites

Python 3.11+ and a local virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e '.[dev]'
python -m playwright install chromium
cp .env.example .env
```

Playwright requires its matching browser binaries to be installed separately.

## Run the demo app

In terminal 1:

```bash
uvicorn demo_app.app:app --reload --port 8000
```

Open http://127.0.0.1:8000 . Search for `12345` or `67890`.

## Phase 3: deterministic replay

In terminal 2:

```bash
python -m app.replay.cli artifacts/lookup_member_balance.v1.json --member-id 12345
```

Expected result contains:

```json
{
  "status": "success",
  "outputs": {
    "savings_balance": 12450.5
  }
}
```

Business-outcome path:

```bash
python -m app.replay.cli artifacts/lookup_member_balance.v1.json --member-id 99999
```

This should return `business_outcome` / `MEMBER_NOT_FOUND` rather than crashing.

## Phase 6: capability interface

In terminal 3:

```bash
uvicorn app.main:app --reload --port 9000
```

Discover:

```bash
curl http://127.0.0.1:9000/capabilities
```

Invoke:

```bash
curl -X POST http://127.0.0.1:9000/capabilities/lookup_member_balance/invoke \\
  -H 'Content-Type: application/json' \\
  -d '{"inputs":{"member_id":"12345"}}'
```

Generate runnable code:

```bash
curl -X POST http://127.0.0.1:9000/capabilities/lookup_member_balance/generate
```

Or:

```bash
python -m app.generator.cli artifacts/lookup_member_balance.v1.json
```

The generated test is written to `generated/`. The generator uses the artifact as its only source of truth. It is designed to run with the Playwright Pytest plugin.

## Phase 4: genuine LLM discovery

Set `OPENAI_API_KEY` and optionally change `OPENAI_MODEL` in `.env`.

Start the demo app first, then:

```bash
python -m app.agent.cli "Look up member 12345 and return their savings balance"
```

The discovery run is saved under `evidence/discovery/<run-id>/` and the artifact under `artifacts/`.

## Simulated transient error

For a manual UI demo, restart the demo app with:

```bash
SIMULATE_TRANSIENT_ERROR=true uvicorn demo_app.app:app --reload --port 8000
```

## Tests

```bash
pytest -q
```

## Human handoff seam

For the take-home, the handoff manager models the required control-transfer state machine and exposes the corresponding API. Full remote co-browsing is intentionally cut; the production seam is a persistent browser/session manager plus an operator surface controlling the same browser context.

The API exposes pause/control state transitions:

```text
AUTOMATING -> HUMAN_CONTROL -> RESUME_REQUESTED -> AUTOMATING
```

The current take-home implementation keeps sessions in memory and is intentionally a minimal handoff seam; a production version would bind the state machine to a persistent browser/session manager and operator surface.

## Deliberate cuts

No Kubernetes, Redis, Kafka, Celery, distributed workers, real banking integration, desktop automation, vector database, or production authentication. These are design extensions, not prerequisites for the vertical slice.
