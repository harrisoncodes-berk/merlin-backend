from typing import List, Optional, Dict
from pydantic import BaseModel

from app.schemas.common import (
    Feature,
    InventoryItem,
    Skill,
    AbilityKey,
    SpellLevel,
    AbilityScores,
    Spell,
)


class SpellSlots(BaseModel):
    max: int
    used: int


class Spellcasting(BaseModel):
    ability: AbilityKey
    slots: Optional[Dict[SpellLevel, SpellSlots]] = None
    spells: List[Spell]
    className: Optional[str] = None


class Character(BaseModel):
    id: str
    name: str
    race: str
    className: str
    background: str
    level: int
    hpCurrent: int
    hpMax: int
    ac: int
    speed: int
    abilities: AbilityScores
    skills: List[Skill] = []
    features: List[Feature] = []
    inventory: List[InventoryItem] = []
    spellcasting: Optional[Spellcasting] = None
