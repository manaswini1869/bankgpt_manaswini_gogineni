import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.artifact.store import ArtifactStore
from app.capability.catalog import CapabilityCatalog
from app.capability.executor import CapabilityExecutor
from app.config import get_settings
from app.generator.playwright import PlaywrightCodeGenerator
from app.handoff.manager import HandoffManager

settings = get_settings()
store = ArtifactStore(settings.artifact_dir)
catalog = CapabilityCatalog(store)
handoff = HandoffManager()


class InvokeRequest(BaseModel):
    inputs: dict = Field(default_factory=dict)
    version: int | None = None


class EscalateRequest(BaseModel):
    reason: str


class ResumeRequest(BaseModel):
    note: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Computer-Use Automation API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/capabilities")
async def capabilities():
    return [
        {
            "name": artifact.id,
            "version": artifact.version,
            "description": artifact.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    name: {"type": param.type.value, "description": param.description}
                    for name, param in artifact.inputs.items()
                },
                "required": [name for name, param in artifact.inputs.items() if param.required],
            },
            "output_schema": {
                name: {"type": param.type.value, "description": param.description}
                for name, param in artifact.outputs.items()
            },
        }
        for artifact in catalog.list()
    ]


@app.post("/capabilities/{name}/invoke")
async def invoke(name: str, request: InvokeRequest):
    executor = CapabilityExecutor(catalog, __import__("app.replay.engine", fromlist=["ReplayEngine"]).ReplayEngine(
        store, settings.evidence_dir, headless=settings.headless
    ))
    try:
        result = await executor.invoke(name, request.inputs, request.version)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.model_dump(mode="json")


@app.post("/capabilities/{name}/generate")
async def generate(name: str, version: int | None = None):
    try:
        artifact = catalog.get(name, version)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    path = PlaywrightCodeGenerator().write(artifact, settings.generated_dir)
    return {"path": str(path), "code": path.read_text()}


@app.post("/runs/{run_id}/escalate")
async def escalate(run_id: str, request: EscalateRequest):
    if run_id not in handoff.sessions:
        handoff.create(run_id)
    session = handoff.escalate(run_id, request.reason)
    return session.__dict__


@app.post("/runs/{run_id}/resume")
async def resume(run_id: str, request: ResumeRequest):
    if run_id not in handoff.sessions:
        raise HTTPException(status_code=404, detail="run not found")
    session = handoff.request_resume(run_id, request.note)
    return session.__dict__


def run():
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
