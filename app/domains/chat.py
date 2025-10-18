from dataclasses import dataclass
from typing import Literal, Optional

from app.domains.adventures import AdventureStatus


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
    adventure_title: str
    story_brief: str
    status: AdventureStatus
    created_at: str
    updated_at: str
    archived_at: Optional[str]
