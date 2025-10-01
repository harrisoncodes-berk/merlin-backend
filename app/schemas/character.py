from typing import List, Optional, Dict
from pydantic import BaseModel, Field

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
    maximum: int = Field(alias="max")
    used: int


class Spellcasting(BaseModel):
    ability: AbilityKey
    slots: Optional[Dict[SpellLevel, SpellSlots]] = None
    spells: List[Spell]  # include cantrips with level = 0
    className: Optional[str] = None


class Character(BaseModel):
    id: str
    name: str  # name
    race: str  # race.name
    className: str  # class.name
    background: str  # background.name
    level: int  # 1
    hpCurrent: int
    hpMax: int  # class.hit_dice.sides + get_ability_bonus(abilities.constitution)
    ac: int  # class.ac
    speed: int  # race.speed
    abilities: AbilityScores  # abilities
    skills: List[Skill] = []  # skills
    features: List[Feature] = []  # race.features + class.features + background.features
    inventory: List[InventoryItem] = []  # background.inventory
    spellcasting: Optional[Spellcasting] = None  # create based on class.spell_choices
