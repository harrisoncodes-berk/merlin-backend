import random

def roll_dice(sides: int) -> int:
    return random.randint(1, sides)

def skill_check(difficulty: int, ability_modifier: int, skill_modifier: int) -> bool:
    return (roll_dice(20) + ability_modifier + skill_modifier) >= difficulty