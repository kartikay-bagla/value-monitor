import os
import time
import traceback
from typing import Optional
from fastapi import HTTPException, Request


def getenv(
    key: str, default: Optional[str] = None
) -> str:
    val = os.getenv(key)
    if val is not None:
        return val
    if default:
        return default
    raise ValueError(f"Environment variable {key} not set.")


def get_secret_key(request: Request, secret_key: str):
    secret_key = request.headers.get("secret-key")
    if secret_key != secret_key:
        raise HTTPException(status_code=400, detail="Invalid secret key")
    return secret_key


def every(delay, task, *args, **kwargs):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task(*args, **kwargs)
        except Exception:
            traceback.print_exc()
        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay
