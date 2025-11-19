import random


def roll_dice(sides: int) -> int:
    """Rolls a dice with the given number of sides.

    Args:
        sides: The number of sides on the dice.

    Returns:
        The result of the dice roll.
    """
    return random.randint(1, sides)


def skill_check(difficulty: int, ability_modifier: int, skill_modifier: int) -> bool:
    """Checks a skill check with the given difficulty, ability modifier, and skill modifier.

    Args:
        difficulty: The difficulty of the skill check.
        ability_modifier: The ability modifier to add to the roll.
        skill_modifier: The skill modifier to add to the roll.

    Returns:
        True if the skill check is successful, False otherwise.
    """
    return (roll_dice(20) + ability_modifier + skill_modifier) >= difficulty
