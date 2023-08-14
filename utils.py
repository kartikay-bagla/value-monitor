import config
from fastapi import HTTPException, Request


def get_secret_key(request: Request):
    secret_key = request.headers.get("secret-key")
    if secret_key != config.SECRET_KEY:
        raise HTTPException(status_code=400, detail="Invalid secret key")
    return secret_key
