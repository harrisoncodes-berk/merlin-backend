import random

from app.domains.character_common import AbilityNameToKey, Skill
from app.domains.character import Character


def roll_dice(sides: int) -> int:
    """Rolls a dice with the given number of sides.

    Args:
        sides: The number of sides on the dice.

    Returns:
        The result of the dice roll.
    """
    return random.randint(1, sides)


def ability_check(
    character: Character, difficulty: int, ability: str, skill: str
) -> str:
    """Checks if an action is successful with the given difficulty, ability modifier, and skill modifier.

    Args:
        difficulty: The difficulty of the action.
        ability: The ability to use for the check.
        skill: The skill to use for the check.

    Returns:
        A message describing the result of the check.
    """
    ability_score = getattr(character.abilities, AbilityNameToKey[ability])
    skill_obj = next((s for s in character.skills if s.key == skill), None)
    successful = (
        roll_dice(20)
        + calculate_ability_modifier(ability_score)
        + calculate_skill_modifier(skill_obj)
    ) >= difficulty
    if successful:
        return "The action was successful."
    return "The action was not successful."


def calculate_ability_modifier(ability_score: int) -> int:
    return (ability_score - 10) // 2


def calculate_skill_modifier(skill: Skill) -> int:
    if skill.expertise:
        return 4
    elif skill.proficient:
        return 2
    else:
        return 0
