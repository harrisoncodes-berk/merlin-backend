from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.domains.character_common import (
    AbilityKey,
    AbilityScores,
    Feature,
    Item,
    SpellLevel,
    Skill,
    Spell,
)


@dataclass
class SpellSlots:
    max: int
    used: int


@dataclass
class Spellcasting:
    ability: AbilityKey
    spells: List[Spell]
    slots: Optional[Dict[SpellLevel, SpellSlots]] = None
    class_name: Optional[str] = None

@dataclass
class Character:
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
    abilities: AbilityScores
    skills: List[Skill] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    inventory: List[Item] = field(default_factory=list)
    spellcasting: Optional[Spellcasting] = None
