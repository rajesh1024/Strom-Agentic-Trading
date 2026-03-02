import re
from typing import Any, Dict

# Patterns for sensitive keys to redact
SENSITIVE_PATTERNS = [
    re.compile(r"password", re.I),
    re.compile(r"secret", re.I),
    re.compile(r"token", re.I),
    re.compile(r"api_key", re.I),
    re.compile(r"key", re.I),
    re.compile(r"private", re.I),
    re.compile(r"jwt", re.I),
]

def sanitize_data(data: Any) -> Any:
    """ recursively redact sensitive information from dictionaries or lists """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(pattern.search(k) for pattern in SENSITIVE_PATTERNS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    else:
        return data
