from typing import Literal, List, Optional
from pydantic import Field

from app.schemas.base import APIBase


class SessionIn(APIBase):
    character_id: str


class SessionOut(APIBase):
    session_id: str
    adventure_title: str
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
