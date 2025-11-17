from app.services.tools.tools import update_adventure_status, roll_dice, skill_check

TOOLS_TO_FUNCTIONS = {
    "update_adventure_status": {
        "function": update_adventure_status,
        "async": True,
    },
    "roll_dice": {
        "function": roll_dice,
        "async": False,
    },
    "skill_check": {
        "function": skill_check,
        "async": False,
    },
}

TOOLS_FOR_LLM = [
    {
        "type": "function",
        "name": "update_adventure_status",
        "description": "Update the adventure status based on the latest user message. Does not require a followup.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "An ongoing summary of what the character has done and what has happened in the story so far.",
                    "max_length": 1000,
                },
                "location": {
                    "type": "string",
                    "description": "A short description of the character's current location.",
                    "max_length": 100,
                },
                "combat_state": {
                    "type": "boolean",
                    "description": "True if the character is in combat, false otherwise.",
                },
            },
            "required": ["summary", "location", "combat_state"],
        },
    },
]
