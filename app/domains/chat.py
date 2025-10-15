from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Message:
    message_id: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: str


@dataclass
class Session:
    session_id: str
    character_id: str
    title: str
    settings: dict
    created_at: str
    updated_at: str
    archived_at: Optional[str]
