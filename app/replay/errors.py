class ReplayError(Exception):
    code = "REPLAY_ERROR"


class BusinessOutcome(ReplayError):
    code = "BUSINESS_OUTCOME"


class RecoverableReplayError(ReplayError):
    code = "RECOVERABLE"


class HardFailure(ReplayError):
    code = "HARD_FAILURE"
