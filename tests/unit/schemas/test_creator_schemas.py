from app.schemas.creator import (
    RaceOut,
    ClassOut,
    HitDiceOut,
    SkillChoiceOut,
)
from app.schemas.character_common import FeatureOut


def test_race_out_camel_dump():
    r = RaceOut(
        id="r1",
        name="Halfling",
        description="Small",
        size="Small",
        speed=25,
        ability_bonuses={"dex": 2},
        features=[FeatureOut(id="f1", name="Lucky", description="Reroll 1s")],
    )
    data = r.model_dump(by_alias=True)
    assert "abilityBonuses" in data
    assert data["features"][0]["name"] == "Lucky"


def test_class_out_nested():
    c = ClassOut(
        id="c1",
        name="Rogue",
        description="Sneaky",
        ac=11,
        hit_dice=HitDiceOut(name="d8", rolls=1, sides=8),
        features=[],
        skill_choices=SkillChoiceOut(
            proficiencies=2, description="Pick two", skills=["stealth", "acrobatics"]
        ),
        weapon_choices=None,
        spell_choices=None,
    )
    d = c.model_dump(by_alias=True)
    assert d["hitDice"]["sides"] == 8
