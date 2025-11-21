from dataclasses import dataclass
from typing import Optional, Literal


AbilityKey = Literal["str", "dex", "con", "int", "wis", "cha"]
AbilityNameToKey = {
    "strength": "str",
    "dexterity": "dex",
    "constitution": "con",
    "intelligence": "int",
    "wisdom": "wis",
    "charisma": "cha",
}
SpellLevel = Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


@dataclass
class AbilityScores:
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int


@dataclass
class Feature:
    id: str
    name: str
    description: str
    uses: Optional[int] = None
    max_uses: Optional[int] = None


@dataclass
class HitDice:
    name: str
    rolls: int
    sides: int


@dataclass
class Item:
    id: str
    name: str
    quantity: int
    weight: float
    description: str
    hit_dice: Optional[int] = None


@dataclass
class Skill:
    key: str
    proficient: bool
    expertise: Optional[bool] = False


@dataclass
class Spell:
    id: str
    name: str
    level: int
    description: str
