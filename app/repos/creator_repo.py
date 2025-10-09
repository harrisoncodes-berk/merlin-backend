from dataclasses import asdict
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.domains.creator import (
    Background,
    Class,
    Race,
)
from app.domains.character import Character
from app.models.character_tables import characters
from app.models.creator_tables import backgrounds, classes, races


class CreatorRepo():
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_race(self, id: str) -> Race:
        stmt = select(races).where(races.c.id == id)
        res = await self.db_session.execute(stmt)
        row = res.mappings().first()
        if not row:
            raise NoResultFound(f"Race with id {id} not found")
        return Race(**row)

    async def get_class(self, id: str) -> Class:
        stmt = select(classes).where(classes.c.id == id)
        res = await self.db_session.execute(stmt)
        row = res.mappings().first()
        if not row:
            raise NoResultFound(f"Class with id {id} not found")
        return Class(**row)

    async def get_background(self, id: str) -> Background:
        stmt = select(backgrounds).where(backgrounds.c.id == id)
        res = await self.db_session.execute(stmt)
        row = res.mappings().first()
        if not row:
            raise NoResultFound(f"Background with id {id} not found")
        return Background(**row)

    async def list_races(self) -> list[Race]:
        stmt = select(
            races.c.id,
            races.c.name,
            races.c.description,
            races.c.size,
            races.c.speed,
            races.c.ability_bonuses,
            races.c.features,
        )
        res = await self.db_session.execute(stmt)
        rows = res.mappings().all()
        return [Race(**r) for r in rows]

    async def list_classes(self) -> list[Class]:
        stmt = select(
            classes.c.id,
            classes.c.name,
            classes.c.description,
            classes.c.ac,
            classes.c.hit_dice,
            classes.c.features,
            classes.c.skill_choices,
            classes.c.weapon_choices,
            classes.c.spell_choices,
        )
        res = await self.db_session.execute(stmt)
        rows = res.mappings().all()
        return [Class(**r) for r in rows]

    async def list_backgrounds(self) -> list[Background]:
        stmt = select(
            backgrounds.c.id,
            backgrounds.c.class_id,
            backgrounds.c.name,
            backgrounds.c.description,
            backgrounds.c.features,
            backgrounds.c.skills,
            backgrounds.c.inventory,
        )
        res = await self.db_session.execute(stmt)
        rows = res.mappings().all()
        return [Background(**r) for r in rows]

    async def create_character(self, user_id: str, character: Character) -> Character:
        character_dict = asdict(character)
        stmt = (
            insert(characters)
            .values(**character_dict, user_id=user_id)
            .returning(
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
        )
        res = await self.db_session.execute(stmt)
        character_row = res.mappings().first()
        if not character_row:
            raise Exception("Failed to create character")

        return Character(**character_row)
