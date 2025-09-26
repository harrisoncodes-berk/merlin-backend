from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import characters
from app.schemas.character import CharacterOut


def _row_to_out(row: dict) -> CharacterOut:
    return CharacterOut(
        id=str(row["id"]),
        name=row["name"],
        race=row["race"],
        className=row["class_name"],
        background=row["background"],
        level=row["level"],
        hpCurrent=row["hp_current"],
        hpMax=row["hp_max"],
        ac=row["ac"],
        speed=row["speed"],
        abilities=row["abilities"] or {},
        skills=row["skills"] or [],
        features=row["features"] or [],
        inventory=row["inventory"] or [],
        spellcasting=row["spellcasting"],
    )


async def list_characters_for_user(
    session: AsyncSession, user_id: str
) -> list[CharacterOut]:
    stmt = (
        select(
            characters.c.id,
            characters.c.name,
            characters.c.race,
            characters.c.class_name,
            characters.c.background,
            characters.c.level,
            characters.c.hp_current,
            characters.c.hp_max,
            characters.c.ac,
            characters.c.speed,
            characters.c.abilities,
            characters.c.skills,
            characters.c.features,
            characters.c.inventory,
            characters.c.spellcasting,
        )
        .where(characters.c.user_id == user_id)
        .order_by(characters.c.updated_at.desc())
    )
    res = await session.execute(stmt)
    rows = res.mappings().all()
    return [_row_to_out(r) for r in rows]


async def get_character_for_user(
    session: AsyncSession, user_id: str, id: str
) -> Optional[CharacterOut]:
    stmt = (
        select(
            characters.c.id,
            characters.c.name,
            characters.c.race,
            characters.c.class_name,
            characters.c.background,
            characters.c.level,
            characters.c.hp_current,
            characters.c.hp_max,
            characters.c.ac,
            characters.c.speed,
            characters.c.abilities,
            characters.c.skills,
            characters.c.features,
            characters.c.inventory,
            characters.c.spellcasting,
        )
        .where((characters.c.user_id == user_id) & (characters.c.id == id))
        .limit(1)
    )
    res = await session.execute(stmt)
    row = res.mappings().first()
    return _row_to_out(row) if row else None
