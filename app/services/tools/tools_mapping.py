from app.services.tools.tools import ability_check

TOOLS_TO_FUNCTIONS = {
    "ability_check": ability_check,
}

TOOLS_FOR_LLM = [
    {
        "type": "function",
        "name": "ability_check",
        "description": "If the user attempts something that could fail and have a meaningful consequence, use this tool to check if the character succeeds.",
        "parameters": {
            "type": "object",
            "properties": {
                "difficulty": {
                    "type": "integer",
                    "description": "The difficulty of the ability check based on the task at hand.",
                },
                "ability": {
                    "type": "string",
                    "description": "The ability to use for the check.",
                    "enum": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
                },
                "skill": {
                    "type": "string",
                    "description": "The skill to use for the check. If no skill is relevant, use 'none'.",
                    "enum": ["acrobatics", "animalHandling", "arcana", "athletics", "deception", "history", "insight", "intimidation", "investigation", "medicine", "nature", "perception", "performance", "persuasion", "religion", "sleightOfHand", "stealth", "survival", "none"],
                }
            },
            "required": ["difficulty", "ability", "skill"],
        },
    },
]
