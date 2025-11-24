from dataclasses import asdict
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.character import Character, Spellcasting
from app.domains.character import AbilityScores, Skill, Feature, Item
from app.models.character_tables import characters
from app.models.chat_tables import chat_sessions


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

    async def get_character_by_character_id(
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

    async def get_character_by_session_id(
        self, user_id: str, session_id: str
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
            .join(chat_sessions, characters.c.id == chat_sessions.c.character_id)
            .where(
                (chat_sessions.c.session_id == session_id)
                & (characters.c.user_id == user_id)
            )
            .limit(1)
        )
        res = await self.db_session.execute(stmt)
        row = res.mappings().first()
        return _row_to_character(row) if row else None

    async def update_character_inventory(
        self, character_id: str, inventory: list[Item]
    ) -> None:
        inventory_dict = [asdict(item) for item in inventory]
        stmt = (
            update(characters)
            .where(characters.c.id == character_id)
            .values(inventory=inventory_dict)
        )
        try:
            await self.db_session.execute(stmt)
        except Exception as e:
            print(f"Error updating character inventory: {e}")
            raise


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
        abilities=AbilityScores(**row["abilities"]),
        skills=[Skill(**skill) for skill in row["skills"]],
        features=[Feature(**feature) for feature in row["features"]],
        inventory=[Item(**item) for item in row["inventory"]],
        spellcasting=Spellcasting(**row["spellcasting"])
        if row["spellcasting"]
        else None,
    )
