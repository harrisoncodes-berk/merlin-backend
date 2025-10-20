import pytest
from datetime import datetime, timezone

from app.domains.character import Character, Spellcasting
from app.domains.character_common import AbilityScores, Skill, Feature, Item, Spell
from app.domains.chat import Message
from app.services.orchestration.prompt_builder import PromptBuilder
from app.adapters.llm.types import PromptPayload


"""
To run the test:
PYTHONPYCACHEPREFIX="$PWD/.pycache" pytest -q tests/unit/services/orchestration/test_prompt_builder.py
"""


@pytest.mark.asyncio
async def test_build_standard_prompt_minimal_domain_models():
    character = Character(
        id="char-1",
        name="Awin",
        race="Elf",
        class_name="Wizard",
        background="Sage",
        level=1,
        hp_current=8,
        hp_max=8,
        ac=12,
        speed=30,
        abilities=AbilityScores(str=8, dex=14, con=10, int=16, wis=10, cha=8),
        skills=[Skill(key="arcana", proficient=True)],
        features=[Feature(id="f1", name="Darkvision", description="See in dark")],
        inventory=[
            Item(
                id="rope",
                name="Rope",
                quantity=1,
                weight=10.0,
                description="50ft hemp rope",
            ),
            Item(
                id="potion",
                name="Healing Potion",
                quantity=2,
                weight=0.5,
                description="Heals",
            ),
        ],
        spellcasting=Spellcasting(
            ability="int",
            spells=[
                Spell(
                    id="magic_missile", name="Magic Missile", level=1, description=""
                ),
                Spell(id="shield", name="Shield", level=1, description=""),
            ],
        ),
    )

    now = datetime.now(timezone.utc)
    messages = [
        Message(message_id=1, role="user", content="Hello", created_at=now),
        Message(
            message_id=2, role="assistant", content="Hi adventurer", created_at=now
        ),
        Message(message_id=3, role="user", content="Open the door", created_at=now),
    ]

    builder = PromptBuilder()
    payload = builder.build_standard_prompt(character=character, messages=messages)

    assert isinstance(payload, PromptPayload)

    assert len(payload.system_messages) == 2
    assert any("Dungeon Master" in sm for sm in payload.system_messages)
    assert any("Output Schema" in sm for sm in payload.system_messages)

    assert len(payload.user_messages) == 3
    assert any("## Character Sheet" in um for um in payload.user_messages)
    assert any("Name: Awin" in um for um in payload.user_messages)
    assert any(
        "Abilities: STRENGTH 8  DEXTERITY 14  CONSTITUTION 10  INTELLIGENCE 16  WISDOM 10  CHARISMA 8"
        in um
        for um in payload.user_messages
    )
    assert any("Skills: arcana" in um for um in payload.user_messages)
    assert any(
        "Features: Darkvision: See in dark" in um for um in payload.user_messages
    )
    sheet = next(um for um in payload.user_messages if "## Character Sheet" in um)
    assert "Inventory: " in sheet and "Rope" in sheet and "Healing Potion x2" in sheet
    assert any(
        "Spellcasting: Ability: int | Spells: Magic Missile, Shield" in um
        for um in payload.user_messages
    )
    conv = next(um for um in payload.user_messages if "## Conversation" in um)
    assert "USER: Hello" in conv
    assert "ASSISTANT: Hi adventurer" in conv
    assert "USER: Open the door" in conv
    assert (
        conv.index("USER: Hello")
        < conv.index("ASSISTANT: Hi adventurer")
        < conv.index("USER: Open the door")
    )
    assert any("Respond ONLY with a JSON object" in um for um in payload.user_messages)
