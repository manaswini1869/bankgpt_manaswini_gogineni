from typing import Literal
from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    action: Literal["navigate", "click", "fill", "wait", "finish", "escalate"]
    strategy: Literal["test_id", "role", "label", "text", "css"] | None = None
    value: str | None = None
    name: str | None = None
    target: str | None = None
    reason: str = Field(min_length=1)


class AgentDecision(BaseModel):
    action: AgentAction
    goal_complete: bool = False
