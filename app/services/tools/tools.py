import random

from app.domains.character_common import Skill


def roll_dice(sides: int) -> int:
    """Rolls a dice with the given number of sides.

    Args:
        sides: The number of sides on the dice.

    Returns:
        The result of the dice roll.
    """
    return random.randint(1, sides)


def ability_check(difficulty: int, ability_score: int, skill: Skill) -> bool:
    """Checks if an action is successful with the given difficulty, ability modifier, and skill modifier.

    Args:
        difficulty: The difficulty of the action.
        ability_score: The ability score to use for the check.
        skill: The skill to use for the check.

    Returns:
        True if the action is successful, False otherwise.
    """
    return (
        roll_dice(20)
        + calculate_ability_modifier(ability_score)
        + calculate_skill_modifier(skill)
    ) >= difficulty


def calculate_ability_modifier(ability_score: int) -> int:
    return (ability_score - 10) // 2


def calculate_skill_modifier(skill: Skill) -> int:
    if skill.expertise:
        return 4
    elif skill.proficient:
        return 2
    else:
        return 0
