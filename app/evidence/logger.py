import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.safety.redaction import redact


class EvidenceLogger:
    def __init__(self, root: Path, kind: str, run_id: str | None = None):
        self.run_id = run_id or str(uuid4())
        self.path = root / kind / self.run_id
        self.path.mkdir(parents=True, exist_ok=True)
        self.events_file = self.path / "events.jsonl"

    def event(self, event_type: str, **data) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "run_id": self.run_id,
            **redact(data),
        }
        with self.events_file.open("a") as f:
            f.write(json.dumps(payload, default=str) + "\n")

    def save_json(self, name: str, payload) -> Path:
        path = self.path / name
        path.write_text(json.dumps(redact(payload), indent=2, default=str) + "\n")
        return path
