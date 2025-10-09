from app.domains.character import Character, Spellcasting, SpellSlots
from app.domains.character_common import AbilityScores, Spell


def test_character_defaults_and_spellcasting():
    c = Character(
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
        abilities=AbilityScores(str=8, dex=14, con=10, int=16, wis=10, cha=8),
    )
    assert c.skills == []
    assert c.features == []
    assert c.inventory == []
    assert c.spellcasting is None

    c.spellcasting = Spellcasting(
        ability="int",
        spells=[Spell(id="mm", name="Magic Missile", level=1, description="")],
        slots={"1": SpellSlots(max=2, used=0)},
        class_name="Wizard",
    )
    assert c.spellcasting.ability == "int"
    assert c.spellcasting.slots["1"].max == 2
