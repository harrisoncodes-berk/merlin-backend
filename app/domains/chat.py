from datetime import datetime
from typing import Literal, Optional


class Message:
    message_id: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime


class Session:
    session_id: str
    character_id: str
    title: str
    settings: dict
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
