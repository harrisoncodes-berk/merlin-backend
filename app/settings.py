from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # General
    project_name: str = "merlin-backend"
    version: str = "0.1.0"
    env: str = Field(default="dev", description="Environment name: dev|staging|prod")

    # API
    api_v1_prefix: str = "/v1"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",          # load from .env if present
        env_prefix="",
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
