from app.artifact.store import ArtifactStore


class CapabilityCatalog:
    def __init__(self, store: ArtifactStore):
        self.store = store

    def list(self):
        return self.store.list()

    def get(self, capability_id: str, version: int | None = None):
        return self.store.load(capability_id, version)
