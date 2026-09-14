from app.artifact.schema import RunResult
from app.replay.engine import ReplayEngine


class CapabilityExecutor:
    def __init__(self, catalog, replay_engine):
        self.catalog = catalog
        self.replay_engine: ReplayEngine = replay_engine

    async def invoke(self, capability_id: str, inputs: dict, version: int | None = None) -> RunResult:
        artifact = self.catalog.get(capability_id, version)
        return await self.replay_engine.run(artifact, inputs)
