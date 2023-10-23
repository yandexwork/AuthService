from pydantic_settings import BaseSettings
from pydantic import Field


class Setting(BaseSettings):
    DB_URL: str


settings = Setting()

