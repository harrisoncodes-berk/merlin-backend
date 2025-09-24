from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    project_name: str = "merlin-backend"
    version: str = "0.1.0"
    env: str = Field(default="dev", description="Environment name: dev|staging|prod")

    api_v1_prefix: str = "/v1"
    cors_origins: List[str] = ["http://localhost:5173"]

    database_url: str
    db_ssl_root_cert: Optional[str] = None

    supabase_jwks_url: Optional[str] = None
    supabase_issuer: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
