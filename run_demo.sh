#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
uvicorn demo_app.app:app --reload --reload-dir demo_app --port 8000
