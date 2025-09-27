from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import Feature, InventoryItem, Skill


class AbilityScores(BaseModel):
    strength: int = Field(alias="str")
    dexterity: int = Field(alias="dex")
    constitution: int = Field(alias="con")
    intelligence: int = Field(alias="int")
    wisdom: int = Field(alias="wis")
    charisma: int = Field(alias="cha")


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
