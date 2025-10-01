from typing import List, Optional
from pydantic import BaseModel

from app.schemas.common import (
    Feature,
    InventoryItem,
    Skill,
    AbilityKey,
    AbilityScores,
    Spell,
)


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
    classId: str
    name: str
    description: str
    features: Optional[List[Feature]]
    skills: Optional[List[Skill]]
    inventory: Optional[List[InventoryItem]]


class CharacterDraft(BaseModel):
    name: str
    classId: str
    raceId: str
    backgroundId: str
    skills: List[Skill]
    weapons: List[Weapon]
    spells: List[Spell]
    abilities: AbilityScores
