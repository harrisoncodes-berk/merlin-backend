# tests/unit/schemas/test_character_schemas.py
from app.schemas.character import CharacterOut, SpellcastingOut, SpellSlotsOut
from app.schemas.character_common import (
    AbilityScoresOut,
    FeatureOut,
    ItemOut,
    SkillOut,
    SpellOut,
)


def test_character_out_aliases_and_dump():
    ch = CharacterOut(
        id="id1",
        name="Awin",
        race="Elf",
        class_name="Wizard",
        background="Sage",
        level=1,
        hp_current=6,
        hp_max=6,
        ac=12,
        speed=30,
        abilities=AbilityScoresOut(str=8, dex=14, con=10, int=16, wis=10, cha=8),
        skills=[SkillOut(key="stealth", proficient=True)],
        features=[
            FeatureOut(id="f1", name="Keen Senses", description="Perception prof.")
        ],
        inventory=[
            ItemOut(id="rope", name="Rope", quantity=1, weight=10.0, description="")
        ],
        spellcasting=SpellcastingOut(
            ability="int",
            slots={"1": SpellSlotsOut(max=2, used=0)},
            spells=[SpellOut(id="mm", name="Magic Missile", level=1, description="")],
            class_name="Wizard",
        ),
    )
    data = ch.model_dump(by_alias=True)
    # camelCase check
    assert "hpCurrent" in data and data["hpCurrent"] == 6
    assert "className" in data and data["className"] == "Wizard"
    assert "spellcasting" in data
    assert "abilities" in data and data["abilities"]["dex"] == 14
