from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import TIMESTAMP, text

from app.adapters.db import metadata

races = Table(
    "races",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("size", String, nullable=False),
    Column("speed", Integer, nullable=False),
    Column("ability_bonuses", JSONB, nullable=True),
    Column("features", JSONB, nullable=True),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    ),
)

classes = Table(
    "classes",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("ac", Integer, nullable=False),
    Column("hit_dice", Integer, nullable=False),
    Column("features", JSONB, nullable=True),
    Column("skill_choices", JSONB, nullable=True),
    Column("weapon_choices", JSONB, nullable=True),
    Column("spell_choices", JSONB, nullable=True),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    ),
)

backgrounds = Table(
    "backgrounds",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("class_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("features", JSONB, nullable=True),
    Column("skills", JSONB, nullable=True),
    Column("inventory", JSONB, nullable=True),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    ),
)
