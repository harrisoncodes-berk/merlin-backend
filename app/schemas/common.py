from typing import Optional
from pydantic import BaseModel


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


class InventoryItem(BaseModel):
    id: str
    name: str
    quantity: int
    weight: Optional[float] = None
    description: Optional[str] = None
