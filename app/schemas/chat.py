from typing import Literal, Optional, List, Dict, Any
from pydantic import Field

from app.schemas.base import APIBase


class SessionIn(APIBase):
    character_id: str
    title: Optional[str] = Field(None, max_length=120)
    settings: Dict[str, Any] = Field(default_factory=dict)


class SessionOut(APIBase):
    session_id: str
    character_id: str
    title: str
    settings: Dict[str, Any]
    created_at: str
    updated_at: str
    archived_at: Optional[str] = None


class MessageOut(APIBase):
    message_id: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: str


class MessageHistoryOut(APIBase):
    session_id: str
    messages: List[MessageOut]
    has_more: bool


class SendMessageIn(APIBase):
    message: str = Field(..., min_length=1, max_length=8000)
