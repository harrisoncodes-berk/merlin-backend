from typing import List, Optional
from pydantic import BaseModel

from app.schemas.common import Feature, InventoryItem, Skill


class AbilityScores(BaseModel):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int


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
    spellcasting: Optional[dict] = None
