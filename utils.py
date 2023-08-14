import os
from typing import Optional


def getenv(
    key: str, default: Optional[str] = None
) -> str:
    val = os.getenv(key)
    if val is not None:
        return val
    if default:
        return default
    raise ValueError(f"Environment variable {key} not set.")
