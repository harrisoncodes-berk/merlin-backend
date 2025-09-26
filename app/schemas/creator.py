from typing import List, Optional
from pydantic import BaseModel

from app.schemas.common import Feature, InventoryItem, Skill


class AbilityBonuses(BaseModel):
    str: Optional[int] = None
    dex: Optional[int] = None
    con: Optional[int] = None
    int: Optional[int] = None
    wis: Optional[int] = None
    cha: Optional[int] = None


class Race(BaseModel):
    id: str
    name: str
    description: str
    size: str
    speed: int
    abilityBonuses: AbilityBonuses
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
    features: List[Feature] = []
    skillChoices: SkillChoice
    weaponChoices: List[WeaponChoice]
    spellChoices: List[SpellChoice]


class Background(BaseModel):
    id: str
    name: str
    description: str
    features: List[Feature] = []
    skills: List[Skill] = []
    inventory: List[InventoryItem] = []
