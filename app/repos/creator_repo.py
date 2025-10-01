from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.models.tables import backgrounds, classes, races, characters
from app.schemas.creator import (
    Background,
    Class,
    Race,
    Weapon,
    WeaponChoice,
    CharacterDraft,
)
from app.schemas.character import Character, Spellcasting, SpellSlots
from uuid import uuid4


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
            weapon_choices.append(
                WeaponChoice(
                    id=str(weapon_choice["id"]),
                    name=weapon_choice["name"],
                    number=weapon_choice["number"],
                    description=weapon_choice["description"],
                    choices=choices,
                )
            )
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


def _background_row_to_out(row: dict) -> Background:
    return Background(
        id=str(row["id"]),
        classId=str(row["class_id"]),
        name=row["name"],
        description=row["description"],
        features=row["features"] or None,
        skills=row["skills"] or None,
        inventory=row["inventory"] or None,
    )


async def list_backgrounds(session: AsyncSession) -> list[Background]:
    stmt = select(
        backgrounds.c.id,
        backgrounds.c.class_id,
        backgrounds.c.name,
        backgrounds.c.description,
        backgrounds.c.features,
        backgrounds.c.skills,
        backgrounds.c.inventory,
    )
    res = await session.execute(stmt)
    rows = res.mappings().all()
    return [_background_row_to_out(r) for r in rows]


def _row_to_character(row: dict) -> Character:
    return Character(
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


async def create_character(
    session: AsyncSession, user_id: str, character_draft: CharacterDraft
) -> Character:
    """Create a new character from a character draft."""

    # Get race data
    race_stmt = select(races).where(races.c.id == character_draft.raceId)
    race_result = await session.execute(race_stmt)
    race_row = race_result.mappings().first()
    if not race_row:
        raise NoResultFound(f"Race with id {character_draft.raceId} not found")

    # Get class data
    class_stmt = select(classes).where(classes.c.id == character_draft.classId)
    class_result = await session.execute(class_stmt)
    class_row = class_result.mappings().first()
    if not class_row:
        raise NoResultFound(f"Class with id {character_draft.classId} not found")

    # Get background data
    background_stmt = select(backgrounds).where(
        backgrounds.c.id == character_draft.backgroundId
    )
    background_result = await session.execute(background_stmt)
    background_row = background_result.mappings().first()
    if not background_row:
        raise NoResultFound(
            f"Background with id {character_draft.backgroundId} not found"
        )

    # Calculate derived stats
    con_modifier = (character_draft.abilities.con - 10) // 2
    dex_modifier = (character_draft.abilities.dex - 10) // 2

    # Calculate HP (class hit dice + con modifier)
    hit_dice = class_row["hit_dice"]
    hp_max = hit_dice["sides"] + con_modifier  # Level 1: max roll + con mod

    # Calculate AC (class base AC + dex modifier, max dex bonus typically applies)
    ac = class_row["ac"] + dex_modifier

    # Use race speed
    speed = race_row["speed"]

    # Prepare spellcasting data
    spellcasting_data = None
    if character_draft.spells:
        spellcasting_data = Spellcasting(
            ability="int",  # Default to intelligence for now
            slots={
                1: SpellSlots(
                    maximum=2,
                    used=0,
                ),
            },
            spells=character_draft.spells,
        ).model_dump()

    # Prepare inventory (convert weapons to inventory items)
    inventory = []
    for weapon in character_draft.weapons:
        inventory.append(
            {
                "id": weapon.id,
                "name": weapon.name,
                "quantity": 1,
                "description": weapon.description,
            }
        )
    for background_item in background_row["inventory"]:
        inventory.append(
            {
                "id": background_item["id"],
                "name": background_item["name"],
                "quantity": background_item["quantity"],
                "description": background_item["description"],
            }
        )

    # Insert character
    insert_stmt = (
        insert(characters)
        .values(
            id=uuid4(),
            user_id=user_id,
            name=character_draft.name,
            race=race_row["name"],
            class_name=class_row["name"],
            background=background_row["name"],
            level=1,
            hp_current=hp_max,
            hp_max=hp_max,
            ac=ac,
            speed=speed,
            abilities=character_draft.abilities.model_dump(),
            skills=[skill.model_dump() for skill in character_draft.skills],
            features=(race_row["features"] or [])
            + (class_row["features"] or [])
            + (background_row["features"] or []),
            inventory=(inventory or [] + (background_row["inventory"] or [])),
            spellcasting=spellcasting_data,
        )
        .returning(characters)
    )

    result = await session.execute(insert_stmt)
    character_row = result.mappings().first()

    # Commit the transaction
    await session.commit()

    # Convert to Character schema
    return _row_to_character(character_row)
