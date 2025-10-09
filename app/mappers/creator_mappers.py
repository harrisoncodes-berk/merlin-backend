from app.domains.character_common import (
    AbilityScores,
    Item,
    Skill,
    Spell,
)
from app.domains.creator import CreateCharacterCommand
from app.schemas.creator import CreateCharacterIn


def create_character_in_to_command(
    create_character_in: CreateCharacterIn,
) -> CreateCharacterCommand:
    return CreateCharacterCommand(
        name=create_character_in.name,
        class_id=create_character_in.class_id,
        race_id=create_character_in.race_id,
        background_id=create_character_in.background_id,
        skills=[Skill(**s.model_dump()) for s in (create_character_in.skills or [])],
        weapons=[Item(**w.model_dump()) for w in (create_character_in.weapons or [])],
        spells=[Spell(**sp.model_dump()) for sp in (create_character_in.spells or [])],
        abilities=AbilityScores(**create_character_in.abilities.model_dump()),
    )
