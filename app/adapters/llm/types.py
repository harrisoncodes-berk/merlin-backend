from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PromptPayload(BaseModel):
    system_messages: List[str] = Field(default_factory=list)
    user_messages: List[str] = Field(default_factory=list)


class LLMResult(BaseModel):
    text: str
    finish_reason: Optional[str] = None
    raw: Dict = Field(default_factory=dict)
