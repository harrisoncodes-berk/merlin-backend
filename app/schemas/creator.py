from typing import List, Optional
from app.schemas.base import APIBase

from app.schemas.character_common import (
    AbilityKey,
    AbilityScoresOut,
    FeatureOut,
    ItemOut,
    SkillOut,
    SpellOut,
)


class RaceOut(APIBase):
    id: str
    name: str
    description: str
    size: str
    speed: int
    ability_bonuses: dict[AbilityKey, int]
    features: List[FeatureOut] = []


class SkillChoiceOut(APIBase):
    proficiencies: int
    expertise: Optional[int] = None
    description: str
    skills: List[str] = []


class HitDiceOut(APIBase):
    name: str
    rolls: int
    sides: int


class ChoiceOut(APIBase):
    id: str
    name: str
    number: int
    description: str
    choices: List[ItemOut] | List[SpellOut]


class ClassOut(APIBase):
    id: str
    name: str
    description: str
    ac: int
    hit_dice: HitDiceOut
    features: Optional[List[FeatureOut]]
    skill_choices: Optional[SkillChoiceOut]
    weapon_choices: Optional[List[ChoiceOut]]
    spell_choices: Optional[List[ChoiceOut]]


class BackgroundOut(APIBase):
    id: str
    class_id: str
    name: str
    description: str
    features: Optional[List[FeatureOut]]
    skills: Optional[List[SkillOut]]
    inventory: Optional[List[ItemOut]]


class CreateCharacterIn(APIBase):
    name: str
    class_id: str
    race_id: str
    background_id: str
    skills: List[SkillOut]
    weapons: List[ItemOut]
    spells: List[SpellOut]
    abilities: AbilityScoresOut
