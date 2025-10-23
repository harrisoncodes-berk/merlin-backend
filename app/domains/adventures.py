from dataclasses import dataclass

@dataclass
class AdventureStatus:
    summary: str
    location: str
    combat_state: bool


@dataclass
class Adventure:
    adventure_id: str
    title: str
    story_brief: str
    starting_status: AdventureStatus
