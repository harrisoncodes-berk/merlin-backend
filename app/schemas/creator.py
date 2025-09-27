from typing import List, Literal, Optional
from pydantic import BaseModel

from app.schemas.common import Feature, InventoryItem, Skill

AbilityKey = Literal["str", "dex", "con", "int", "wis", "cha"]


class Race(BaseModel):
    id: str
    name: str
    description: str
    size: str
    speed: int
    abilityBonuses: dict[AbilityKey, int]
    features: List[Feature] = []


class SkillChoice(BaseModel):
    proficiencies: int
    expertise: Optional[int] = None
    description: str
    skills: List[str] = []


class HitDice(BaseModel):
    name: str
    rolls: int
    sides: int


class Weapon(BaseModel):
    id: str
    name: str
    description: str
    hitDice: HitDice


class WeaponChoice(BaseModel):
    id: str
    name: str
    number: int
    description: str
    choices: List[Weapon]


class Spell(BaseModel):
    id: str
    name: str
    level: int
    description: str


class SpellChoice(BaseModel):
    id: str
    name: str
    number: int
    description: str
    choices: List[Spell]


class Class(BaseModel):
    id: str
    name: str
    description: str
    ac: int
    hitDice: HitDice
    features: Optional[List[Feature]]
    skillChoices: Optional[SkillChoice]
    weaponChoices: Optional[List[WeaponChoice]]
    spellChoices: Optional[List[SpellChoice]]


class Background(BaseModel):
    id: str
    name: str
    description: str
    features: Optional[List[Feature]]
    skills: Optional[List[Skill]]
    inventory: Optional[List[InventoryItem]]
