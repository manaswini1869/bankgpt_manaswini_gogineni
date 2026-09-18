from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    EXTRACT = "extract"
    WAIT = "wait"


class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"


class RiskLevel(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    RISKY = "risky"


class RunStatus(str, Enum):
    SUCCESS = "success"
    BUSINESS_OUTCOME = "business_outcome"
    RECOVERABLE = "recoverable"
    FAILED = "failed"
    ESCALATED = "escalated"


class Locator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: Literal["test_id", "role", "label", "text", "css"]
    value: str
    name: str | None = None
    rationale: str | None = None


class Target(BaseModel):
    locator: Locator


class InputParameter(BaseModel):
    type: ParameterType
    description: str
    required: bool = True
    default: Any | None = None


class OutputParameter(BaseModel):
    type: ParameterType
    description: str


class Step(BaseModel):
    id: str
    action: ActionType
    target: Target | None = None
    value: str | None = None
    output: str | None = None
    timeout_ms: int = Field(default=5000, ge=100, le=120_000)
    retry_count: int = Field(default=1, ge=0, le=5)

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 10_000:
            raise ValueError("step value is too large")
        return value


class Checkpoint(BaseModel):
    strategy: Literal["text", "locator", "url"]
    expected: str


class Policy(BaseModel):
    allowed_actions: list[ActionType]
    allowed_domains: list[str]
    risk: RiskLevel = RiskLevel.READ_ONLY


class OutcomeMarkers(BaseModel):
    business: dict[str, str] = Field(default_factory=dict)
    recoverable: dict[str, str] = Field(default_factory=dict)


class CapabilityArtifact(BaseModel):
    schema_version: str = "1.0"
    id: str
    version: int = Field(ge=1)
    name: str
    description: str
    target_app: str
    entrypoint: str
    inputs: dict[str, InputParameter] = Field(default_factory=dict)
    outputs: dict[str, OutputParameter] = Field(default_factory=dict)
    steps: list[Step] = Field(min_length=1)
    checkpoint: Checkpoint
    policy: Policy
    outcome_markers: OutcomeMarkers = Field(default_factory=OutcomeMarkers)


class RunResult(BaseModel):
    status: RunStatus
    capability_id: str
    capability_version: int
    step_id: str | None = None
    outputs: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str | None = None
    evidence_path: str | None = None
    run_id: str | None = None
