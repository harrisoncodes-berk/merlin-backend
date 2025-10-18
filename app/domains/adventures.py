import dataclasses


@dataclasses.dataclass()
class AdventureStatus:
    status: str
    location: str
    combat_state: bool


@dataclasses.dataclass()
class Adventure:
    adventure_id: str
    title: str
    story_brief: str
    starting_status: AdventureStatus
