class ReplayError(Exception):
    code = "REPLAY_ERROR"


class BusinessOutcome(ReplayError):
    code = "BUSINESS_OUTCOME"


class MemberNotFound(BusinessOutcome):
    code = "MEMBER_NOT_FOUND"


class RecoverableReplayError(ReplayError):
    code = "RECOVERABLE"


class HardFailure(ReplayError):
    code = "HARD_FAILURE"
