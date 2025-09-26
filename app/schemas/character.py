from typing import List, Optional
from pydantic import BaseModel


class AbilityScores(BaseModel):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int


class Skill(BaseModel):
    key: str
    proficient: bool
    expertise: Optional[bool] = False


class Feature(BaseModel):
    id: str
    name: str
    summary: Optional[str] = None
    uses: Optional[int] = None
    maxUses: Optional[int] = None


class InventoryItem(BaseModel):
    id: str
    name: str
    quantity: int
    weight: Optional[float] = None
    description: Optional[str] = None


class CharacterOut(BaseModel):
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
