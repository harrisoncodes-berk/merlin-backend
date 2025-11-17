import json
import random

from app.domains.adventures import AdventureStatus
from app.repos.chat_repo import ChatRepo


async def update_adventure_status(chat_repo: ChatRepo, session_id: str, result_text: str):
    """Updates the adventure status for the given session based on the current turn.
    
    Args:
        chat_repo: The chat repository to update the adventure status.
        session_id: The session ID to update the adventure status for.
        result_text: The result text from the LLM to update the adventure status from.
    """
    adventure_status = json.loads(result_text).get("adventure_status")
    await chat_repo.update_session_adventure_status(
        session_id, AdventureStatus(**adventure_status)
    )

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