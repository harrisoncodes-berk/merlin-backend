from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.character import Character
from app.models.character_tables import characters


class CharacterRepo:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def list_characters_for_user(self, user_id: str) -> list[Character]:
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
        res = await self.db_session.execute(stmt)
        rows = res.mappings().all()
        return [_row_to_character(r) for r in rows]

    async def get_character_for_user(
        self, user_id: str, id: str
    ) -> Optional[Character]:
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
        res = await self.db_session.execute(stmt)
        row = res.mappings().first()
        return _row_to_character(row) if row else None

def _row_to_character(row: dict) -> Character:
    return Character(
        id=str(row["id"]),
        name=row["name"],
        race=row["race"],
        class_name=row["class_name"],
        background=row["background"],
        level=row["level"],
        hp_current=row["hp_current"],
        hp_max=row["hp_max"],
        ac=row["ac"],
        speed=row["speed"],
        abilities=row["abilities"],
        skills=row["skills"],
        features=row["features"],
        inventory=row["inventory"],
        spellcasting=row["spellcasting"],
    )