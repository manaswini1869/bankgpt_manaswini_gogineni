import re

SENSITIVE_KEY_PATTERN = re.compile(r"(password|secret|token|authorization|ssn|account_number|api_key)", re.I)


def redact(value):
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if SENSITIVE_KEY_PATTERN.search(k) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", value)
    return value
