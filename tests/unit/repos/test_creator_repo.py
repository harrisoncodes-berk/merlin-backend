import pytest
from unittest.mock import AsyncMock
from dataclasses import asdict

from app.domains.character import Character
from app.domains.character_common import AbilityScores
from app.repos.creator_repo import CreatorRepo

from tests.helpers.sqlalchemy_fakes import FakeResult


@pytest.mark.asyncio
async def test_list_races_uses_session_and_maps_rows():
    session = AsyncMock()
    # rows look like what your SELECT returns
    rows = [
        {
            "id": "race-1",
            "name": "Elf",
            "description": "Graceful",
            "size": "Medium",
            "speed": 30,
            "ability_bonuses": {"dex": 2},
            "features": [],
        }
    ]
    session.execute.return_value = FakeResult(rows)

    repo = CreatorRepo(session)
    races = await repo.list_races()

    assert len(races) == 1
    assert races[0].name == "Elf"
    session.execute.assert_called_once()  # we exercised SQL path


@pytest.mark.asyncio
async def test_get_race_handles_not_found():
    session = AsyncMock()
    session.execute.return_value = FakeResult([])  # no rows
    repo = CreatorRepo(session)

    from sqlalchemy.exc import NoResultFound

    with pytest.raises(NoResultFound):
        await repo.get_race("missing")


@pytest.mark.asyncio
async def test_create_character_inserts_and_returns_mapped_character():
    session = AsyncMock()
    # emulate DB returning created row (same as inserted)
    returned = [
        {
            "id": "char-1",
            "name": "Awin",
            "race": "Elf",
            "class_name": "Wizard",
            "background": "Sage",
            "level": 1,
            "hp_current": 6,
            "hp_max": 6,
            "ac": 12,
            "speed": 30,
            "abilities": asdict(AbilityScores(8, 14, 10, 16, 10, 8)),
            "skills": [],
            "features": [],
            "inventory": [],
            "spellcasting": None,
        }
    ]
    session.execute.return_value = FakeResult(returned)

    repo = CreatorRepo(session)
    c = Character(
        id="char-1",
        name="Awin",
        race="Elf",
        class_name="Wizard",
        background="Sage",
        level=1,
        hp_current=6,
        hp_max=6,
        ac=12,
        speed=30,
        abilities=AbilityScores(8, 14, 10, 16, 10, 8),
    )
    saved = await repo.create_character("user-1", c)

    assert saved.name == "Awin"
    session.execute.assert_called()  # insert was attempted
