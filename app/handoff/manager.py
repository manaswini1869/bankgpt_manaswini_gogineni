import asyncio
from dataclasses import dataclass

from app.handoff.models import HandoffState


@dataclass
class RunSession:
    run_id: str
    state: HandoffState = HandoffState.AUTOMATING
    reason: str | None = None
    human_note: str | None = None
    resume_event: asyncio.Event | None = None


class HandoffManager:
    def __init__(self):
        self.sessions: dict[str, RunSession] = {}

    def create(self, run_id: str) -> RunSession:
        session = RunSession(run_id=run_id, resume_event=asyncio.Event())
        self.sessions[run_id] = session
        return session

    def escalate(self, run_id: str, reason: str):
        session = self.sessions[run_id]
        session.state = HandoffState.HUMAN_CONTROL
        session.reason = reason
        if session.resume_event:
            session.resume_event.clear()
        return session

    def request_resume(self, run_id: str, note: str | None = None):
        session = self.sessions[run_id]
        session.state = HandoffState.RESUME_REQUESTED
        session.human_note = note
        if session.resume_event:
            session.resume_event.set()
        return session

    async def wait_for_resume(self, run_id: str):
        session = self.sessions[run_id]
        if session.resume_event:
            await session.resume_event.wait()
        session.state = HandoffState.AUTOMATING
        return session

    def get(self, run_id: str):
        return self.sessions[run_id]
