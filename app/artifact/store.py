import json
from pathlib import Path

from app.artifact.schema import CapabilityArtifact


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, capability_id: str, version: int) -> Path:
        return self.root / f"{capability_id}.v{version}.json"

    def save(self, artifact: CapabilityArtifact) -> Path:
        path = self.path_for(artifact.id, artifact.version)
        path.write_text(json.dumps(artifact.model_dump(mode="json"), indent=2) + "\n")
        return path

    def load(self, capability_id: str, version: int | None = None) -> CapabilityArtifact:
        if version is not None:
            path = self.path_for(capability_id, version)
        else:
            paths = sorted(self.root.glob(f"{capability_id}.v*.json"))
            if not paths:
                raise FileNotFoundError(f"No artifact found for {capability_id}")
            path = paths[-1]
        return CapabilityArtifact.model_validate_json(path.read_text())

    def list(self) -> list[CapabilityArtifact]:
        return [CapabilityArtifact.model_validate_json(p.read_text()) for p in sorted(self.root.glob("*.json"))]
