from enum import Enum
from pydantic import BaseModel


class HandoffState(str, Enum):
    AUTOMATING = "automating"
    PAUSED = "paused"
    HUMAN_CONTROL = "human_control"
    RESUME_REQUESTED = "resume_requested"
    COMPLETED = "completed"


class HandoffRequest(BaseModel):
    reason: str


class HandoffRecord(BaseModel):
    run_id: str
    state: HandoffState
    reason: str | None = None
    human_note: str | None = None
