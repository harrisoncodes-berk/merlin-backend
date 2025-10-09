from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.character import Character
from app.domains.character_common import (
    AbilityKey,
    AbilityScores,
    Feature,
    Item,
    Skill,
    Spell,
)


@dataclass
class Race:
    id: str
    name: str
    description: str
    size: str
    speed: int
    ability_bonuses: dict[AbilityKey, int]
    features: List[Feature] = field(default_factory=list)


@dataclass
class SkillChoice:
    proficiencies: int
    description: str
    skills: List[str] = field(default_factory=list)
    expertise: Optional[int] = None


@dataclass
class HitDice:
    name: str
    rolls: int
    sides: int


@dataclass
class Choice:
    id: str
    name: str
    number: int
    description: str
    choices: List[Item] | List[Spell]


@dataclass
class Class:
    id: str
    name: str
    description: str
    ac: int
    hit_dice: HitDice
    features: Optional[List[Feature]]
    skill_choices: Optional[SkillChoice]
    weapon_choices: Optional[List[Choice]]
    spell_choices: Optional[List[Choice]]


@dataclass
class Background:
    id: str
    class_id: str
    name: str
    description: str
    features: Optional[List[Feature]]
    skills: Optional[List[Skill]]
    inventory: Optional[List[Item]]


@dataclass
class CreateCharacterCommand:
    name: str
    class_id: str
    race_id: str
    background_id: str
    skills: List[Skill]
    weapons: List[Item]
    spells: List[Spell]
    abilities: AbilityScores


class CreatorRepo(Protocol):
    db_session: AsyncSession
    async def get_race(self, race_id: str) -> Race: ...
    async def get_class(self, class_id: str) -> Class: ...
    async def get_background(self, background_id: str) -> Background: ...
    async def list_races(self) -> list[Race]: ...
    async def list_classes(self) -> list[Class]: ...
    async def list_backgrounds(self) -> list[Background]: ...
    async def create_character(
        self, user_id: str, character: Character
    ) -> Character: ...
