from app.schemas.base import APIBase
from typing import Dict, List, Optional

from app.schemas.character_common import (
    AbilityKey,
    AbilityScoresOut,
    FeatureOut,
    ItemOut,
    SpellLevel,
    SkillOut,
    SpellOut,
)


class SpellSlotsOut(APIBase):
    max: int
    used: int


class SpellcastingOut(APIBase):
    ability: AbilityKey
    slots: Optional[Dict[SpellLevel, SpellSlotsOut]] = None
    spells: List[SpellOut]
    class_name: Optional[str] = None


class CharacterOut(APIBase):
    id: str
    name: str
    race: str
    class_name: str
    background: str
    level: int
    hp_current: int
    hp_max: int
    ac: int
    speed: int
    abilities: AbilityScoresOut
    skills: List[SkillOut] = []
    features: List[FeatureOut] = []
    inventory: List[ItemOut] = []
    spellcasting: Optional[SpellcastingOut] = None
