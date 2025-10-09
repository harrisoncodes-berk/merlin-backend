# tests/unit/services/character/test_create_character_service.py
import pytest

from app.domains.character import Character, Spellcasting
from app.domains.character_common import AbilityScores, Item, Skill, Spell
from app.domains.creator import (
    Background,
    Class,
    CreateCharacterCommand,
    HitDice,
    Race,
    SkillChoice,
)
from app.services.character.create_character_service import CreateCharacterService

"""
To run the test:
PYTHONPYCACHEPREFIX="$PWD/.pycache" pytest -q tests/unit/services/character/test_create_character_service.py
"""


class _DummySession:
    async def commit(self):  # service calls repo.db_session.commit()
        return None


class FakeCreatorRepo:
    def __init__(self, *, race: Race, klass: Class, background: Background):
        self._race = race
        self._class = klass
        self._background = background
        self.db_session = _DummySession()

    async def get_race(self, race_id: str) -> Race:
        assert race_id == self._race.id
        return self._race

    async def get_class(self, class_id: str) -> Class:
        assert class_id == self._class.id
        return self._class

    async def get_background(self, background_id: str) -> Background:
        assert background_id == self._background.id
        return self._background

    async def create_character(self, user_id: str, character: Character) -> Character:
        assert user_id  # sanity
        return character  # echo back


@pytest.mark.asyncio
async def test_create_character_with_spells():
    race = Race(
        id="race-1",
        name="Elf",
        description="Graceful and agile",
        size="Medium",
        speed=30,
        ability_bonuses={"dex": 2},
        features=[],
    )
    klass = Class(
        id="class-1",
        name="Ranger",
        description="Wilderness warrior",
        ac=12,
        hit_dice=HitDice(name="d10", rolls=1, sides=10),
        features=[],
        skill_choices=SkillChoice(
            proficiencies=2, description="Ranger skills", skills=["stealth", "survival"]
        ),
        weapon_choices=None,
        spell_choices=None,
    )
    background = Background(
        id="bg-1",
        class_id="class-1",
        name="Outlander",
        description="Wanderer of the wilds",
        features=[],
        skills=[],
        inventory=[
            Item(
                id="rope",
                name="Rope",
                quantity=1,
                weight=10.0,
                description="50ft hemp rope",
            )
        ],
    )

    repo = FakeCreatorRepo(race=race, klass=klass, background=background)
    service = CreateCharacterService(creator_repo=repo)  # type: ignore[arg-type]

    command = CreateCharacterCommand(
        name="Arannis",
        class_id="class-1",
        race_id="race-1",
        background_id="bg-1",
        skills=[Skill(key="stealth", proficient=True)],
        weapons=[
            Item(
                id="shortsword",
                name="Shortsword",
                quantity=1,
                weight=2.0,
                description="",
            )
        ],
        spells=[Spell(id="hunter_mark", name="Hunter's Mark", level=1, description="")],
        abilities=AbilityScores(str=10, dex=16, con=14, int=10, wis=12, cha=8),
    )

    character = await service.create_character(
        user_id="user-1", create_character_command=command
    )

    assert character.hp_max == 12  # 10 + con mod 2
    assert character.hp_current == 12
    assert character.ac == 15  # 12 + dex mod 3
    assert character.speed == 30

    names = [i["name"] if isinstance(i, dict) else i.name for i in character.inventory]
    assert {"Shortsword", "Rope"}.issubset(set(names))

    assert character.spellcasting is not None
    assert isinstance(character.spellcasting, Spellcasting)
    assert character.spellcasting.ability == "int"
    assert character.spellcasting.slots["1"].max == 2
    assert character.spellcasting.slots["1"].used == 0
    assert any(s.name == "Hunter's Mark" for s in character.spellcasting.spells)


@pytest.mark.asyncio
async def test_create_character_without_spells():
    race = Race(
        id="race-1",
        name="Human",
        description="Versatile",
        size="Medium",
        speed=30,
        ability_bonuses={"str": 1},
        features=[],
    )
    hit_dice = HitDice(name="d8", rolls=1, sides=8)
    klass = Class(
        id="class-2",
        name="Rogue",
        description="Sneaky attacker",
        ac=11,
        hit_dice=hit_dice,
        features=[],
        skill_choices=None,
        weapon_choices=None,
        spell_choices=None,
    )
    background = Background(
        id="bg-2",
        class_id="class-2",
        name="Criminal",
        description="Underworld",
        features=[],
        skills=[],
        inventory=[],
    )

    repo = FakeCreatorRepo(race=race, klass=klass, background=background)
    service = CreateCharacterService(creator_repo=repo)  # type: ignore[arg-type]

    command = CreateCharacterCommand(
        name="Silas",
        class_id="class-2",
        race_id="race-1",
        background_id="bg-2",
        skills=[],
        weapons=[],
        spells=[],
        abilities=AbilityScores(str=12, dex=14, con=10, int=10, wis=10, cha=10),
    )

    character = await service.create_character(
        user_id="user-2", create_character_command=command
    )

    assert character.hp_max == 8  # 8 + con mod 0
    assert character.hp_current == 8
    assert character.ac == 13  # 11 + dex mod 2
    assert character.speed == 30
    assert character.spellcasting is None
