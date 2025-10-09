from app.domains.character_common import AbilityScores, Feature, Item, Skill, Spell


def test_ability_scores():
    a = AbilityScores(str=8, dex=14, con=12, int=10, wis=10, cha=16)
    assert a.dex == 14


def test_feature_defaults():
    f = Feature(id="f", name="Sneak Attack", description="Extra damage")
    assert f.uses is None
    assert f.max_uses is None


def test_item_and_skill_and_spell():
    i = Item(id="rope", name="Rope", quantity=1, weight=10.0, description="50ft")
    s = Skill(key="stealth", proficient=True, expertise=False)
    sp = Spell(id="mm", name="Magic Missile", level=1, description="pew pew")
    assert i.quantity == 1
    assert s.expertise is False
    assert sp.level == 1
