from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Session(BaseModel):
    sessionId: str
    characterId: str
    title: str
    settings: Dict[str, Any]
    createdAt: str
    updatedAt: str
    archivedAt: Optional[str] = None


class SessionRequest(BaseModel):
    characterId: str
    title: Optional[str] = Field(None, max_length=120)
    settings: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    messageId: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    createdAt: str


class HistoryResponse(BaseModel):
    sessionId: str
    messages: List[Message]
    hasMore: bool


class StreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    clientMessageId: Optional[str] = Field(None, max_length=128)
