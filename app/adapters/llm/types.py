from typing import Optional, Dict
from pydantic import BaseModel, Field


class PromptPayload(BaseModel):
    system_messages: list[str]
    user_messages: list[str]
    tools: list[dict] | None = None


class LLMResult(BaseModel):
    text: str
    finish_reason: Optional[str] = None
    raw: Dict = Field(default_factory=dict)
