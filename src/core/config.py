from pydantic import BaseModel


class DbSettings(BaseModel):
    DB_URL: str = f"postgresql+asyncpg://app:123qwe@localhost:5432/postgres"


settings = DbSettings()