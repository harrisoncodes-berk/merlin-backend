from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import TIMESTAMP, text

metadata = MetaData()

characters = Table(
    "characters",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("name", String, nullable=False),
    Column("race", String, nullable=False),
    Column("class_name", String, nullable=False),
    Column("background", String, nullable=False),
    Column("level", Integer, nullable=False),
    Column("hp_current", Integer, nullable=False),
    Column("hp_max", Integer, nullable=False),
    Column("ac", Integer, nullable=False),
    Column("speed", Integer, nullable=False),
    Column("abilities", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("skills", JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    Column("features", JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    Column("inventory", JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    Column("spellcasting", JSONB, nullable=True),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    ),
)

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