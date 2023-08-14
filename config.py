from fastapi import HTTPException, Request
from utils import getenv

PG_USERNAME = getenv("PG_USERNAME")
PG_PASSWORD = getenv("PG_PASSWORD")
PG_HOST = getenv("PG_HOST")
PG_PORT = getenv("PG_PORT")
PG_DATABASE = getenv("PG_DATABASE")
PG_DATABASE_URL = (
    f"postgresql+psycopg2://{PG_USERNAME}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)
SECRET_KEY = getenv("SECRET_KEY")


def get_secret_key(request: Request):
    secret_key = request.headers.get("secret-key")
    if secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="Invalid secret key")
    return secret_key
