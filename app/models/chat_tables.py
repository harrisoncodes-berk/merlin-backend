from sqlalchemy import (
    Table,
    Column,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from app.adapters.db import metadata

chat_role = ENUM(
    "system",
    "user",
    "assistant",
    "tool",
    name="chat_role",
    create_type=False,
)

chat_sessions = Table(
    "chat_sessions",
    metadata,
    Column("session_id", UUID(as_uuid=False), primary_key=True),
    Column("user_id", UUID(as_uuid=False), nullable=False),
    Column("title", Text, nullable=False),
    Column("settings", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("archived_at", DateTime(timezone=True), nullable=True),
    schema="public",
)

chat_messages = Table(
    "chat_messages",
    metadata,
    Column("message_id", BigInteger, primary_key=True, autoincrement=True),
    Column(
        "session_id",
        UUID(as_uuid=False),
        ForeignKey("public.chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("role", chat_role, nullable=False),
    Column("content", Text, nullable=False),
    Column("tool_name", Text),
    Column("tool_args", JSONB),
    Column("tool_result", JSONB),
    Column("tokens_in", Integer),
    Column("tokens_out", Integer),
    Column("created_at", DateTime(timezone=True), nullable=False),
    schema="public",
)
