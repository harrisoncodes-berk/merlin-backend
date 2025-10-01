from typing import Optional, Literal
from pydantic import BaseModel


AbilityKey = Literal["str", "dex", "con", "int", "wis", "cha"]
SpellLevel = Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


class AbilityScores(BaseModel):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int


class Feature(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    uses: Optional[int] = None
    maxUses: Optional[int] = None


class Skill(BaseModel):
    key: str
    proficient: bool
    expertise: Optional[bool] = False


class Spell(BaseModel):
    id: str
    name: str
    level: int
    description: str


class InventoryItem(BaseModel):
    id: str
    name: str
    quantity: int
    weight: Optional[float] = None
    description: Optional[str] = None
