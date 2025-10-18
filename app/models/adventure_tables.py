from sqlalchemy import Table, Column, String 
from sqlalchemy.dialects.postgresql import JSONB
from app.adapters.db import metadata

adventures = Table(
    "adventures",
    metadata,
    Column("adventure_id", String, primary_key=True),
    Column("title", String, nullable=False),
    Column("story_brief", String, nullable=False),
    Column("starting_status", JSONB, nullable=False),
)