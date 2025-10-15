from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    project_name: str = "merlin-backend"
    version: str = "0.1.0"
    env: str = Field(default="dev", description="Environment name: dev|staging|prod")

    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:5173"]

    database_url: str
    db_ssl_root_cert: Optional[str] = None

    supabase_jwks_url: Optional[str] = None
    supabase_issuer: Optional[str] = None

    llm_provider: str = "noop"
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o-reasoning"
    llm_temperature: float = 0.7
    llm_max_output_tokens: int = 700
    llm_streaming: bool = True
    llm_json_mode: bool = False
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 2
    llm_retry_backoff_ms: int = 250
    llm_circuit_open_threshold: int = 5
    llm_circuit_reset_sec: int = 60
    llm_soft_prompt_budget: int = 6000
    llm_hard_prompt_budget: int = 8000
    enable_tool_calling: bool = True
    enable_rules_rag: bool = False
    enable_safety_filter: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
