from typing import Optional, Literal
from app.schemas.base import APIBase


AbilityKey = Literal["str", "dex", "con", "int", "wis", "cha"]
SpellLevel = Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


class AbilityScoresOut(APIBase):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int


class FeatureOut(APIBase):
    id: str
    name: str
    description: str
    uses: Optional[int] = None
    max_uses: Optional[int] = None


class HitDiceOut(APIBase):
    name: str
    rolls: int
    sides: int


class ItemOut(APIBase):
    id: str
    name: str
    quantity: int
    weight: float
    description: str
    hit_dice: Optional[int] = None


class SkillOut(APIBase):
    key: str
    proficient: bool
    expertise: Optional[bool] = False


class SpellOut(APIBase):
    id: str
    name: str
    level: int
    description: str
