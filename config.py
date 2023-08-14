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
