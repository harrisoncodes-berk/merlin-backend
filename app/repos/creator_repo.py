from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import races, classes
from app.schemas.creator import Race, Class, Weapon, WeaponChoice


def _race_row_to_out(row: dict) -> Race:
    return Race(
        id=str(row["id"]),
        name=row["name"],
        description=row["description"],
        size=row["size"],
        speed=row["speed"],
        abilityBonuses=row["ability_bonuses"] or {},
        features=row["features"] or [],
    )


async def list_races(session: AsyncSession) -> list[Race]:
    stmt = select(
        races.c.id,
        races.c.name,
        races.c.description,
        races.c.size,
        races.c.speed,
        races.c.ability_bonuses,
        races.c.features,
    )
    res = await session.execute(stmt)
    rows = res.mappings().all()
    return [_race_row_to_out(r) for r in rows]

def _weapon_row_to_out(row: dict) -> Weapon:
    return Weapon(
        id=str(row["id"]),
        name=row["name"],
        description=row["description"],
        hitDice=row["hit_dice"],
    )

def _class_row_to_out(row: dict) -> Class:
    if row["weapon_choices"]:
        weapon_choices = []
        for weapon_choice in row["weapon_choices"]:
            choices = []
            for choice in weapon_choice["choices"]:
                choices.append(_weapon_row_to_out(choice))
            weapon_choices.append(WeaponChoice(
                id=str(weapon_choice["id"]),
                name=weapon_choice["name"],
                number=weapon_choice["number"],
                description=weapon_choice["description"],
                choices=choices,
            ))
    else:
        weapon_choices = None
    return Class(
        id=str(row["id"]),
        name=row["name"],
        description=row["description"],
        ac=row["ac"],
        hitDice=row["hit_dice"],
        features=row["features"] or None,
        skillChoices=row["skill_choices"] or None,
        weaponChoices=weapon_choices,
        spellChoices=row["spell_choices"] or None,
    )


async def list_classes(session: AsyncSession) -> list[Class]:
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
    res = await session.execute(stmt)
    rows = res.mappings().all()
    return [_class_row_to_out(r) for r in rows]
