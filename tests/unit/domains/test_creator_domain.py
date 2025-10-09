from app.domains.creator import Race, HitDice, Class, Background
from app.domains.character_common import Feature, Item, Skill


def test_race_domain_defaults():
    r = Race(
        id="r1",
        name="Halfling",
        description="Small and lucky",
        size="Small",
        speed=25,
        ability_bonuses={"dex": 2},
    )
    assert r.features == []


def test_class_domain_shapes():
    hd = HitDice(name="d8", rolls=1, sides=8)
    c = Class(
        id="c1",
        name="Wizard",
        description="Arcane caster",
        ac=10,
        hit_dice=hd,
        features=[],
        skill_choices=None,
        weapon_choices=None,
        spell_choices=None,
    )
    assert c.hit_dice.sides == 8
    assert c.ac == 10


def test_background_domain_inventory_and_skills():
    bg = Background(
        id="b1",
        class_id="c1",
        name="Sage",
        description="Scholar",
        features=[Feature(id="f1", name="Researcher", description="Find lore")],
        skills=[Skill(key="arcana", proficient=True)],
        inventory=[
            Item(id="book", name="Book", quantity=1, weight=1.0, description="Tome")
        ],
    )
    assert bg.inventory[0].name == "Book"
    assert bg.skills[0].key == "arcana"
