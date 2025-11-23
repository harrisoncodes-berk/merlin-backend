from pydantic import BaseModel


class UpdateAdventureStatus(BaseModel):
    summary: str
    location: str
    combat_state: bool


class UpdateInventory(BaseModel):
    item_id: str
    quantity: int


class UpdateHealth(BaseModel):
    hp_current: int
    hp_max: int


class DMResponse(BaseModel):
    message_to_user: str
    update_adventure_status: UpdateAdventureStatus
    update_inventory: UpdateInventory | None = None
    # update_health: UpdateHealth | None = None


DM_RESPONSE_SCHEMA = {
    "format": {
        "type": "json_schema",
        "name": "dm_response_schema",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "message_to_user": {
                    "type": "string",
                    "description": "The message to the user.",
                },
                "update_adventure_status": {
                    "type": "object",
                    "description": "Updates the status of the adventure.",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A brief summary of the adventure so far.",
                        },
                        "location": {
                            "type": "string",
                            "description": "The current location of the character.",
                        },
                        "combat_state": {
                            "type": "boolean",
                            "description": "Whether the character is currently in combat.",
                        },
                    },
                    "required": ["summary", "location", "combat_state"],
                    "additionalProperties": False,
                },
                "update_inventory": {
                    "type": ["object", "null"],
                    "description": "Updates the inventory of the character if an item is gained or lost.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "The action to take with the inventory.",
                            "enum": ["add", "remove"],
                        },
                        "item_id": {
                            "type": "string",
                            "description": "The ID of the item to update.",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "The new quantity of the item.",
                        },
                    },
                    "required": ["action", "item_id", "quantity"],
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
            "required": [
                "message_to_user",
                "update_adventure_status",
                "update_inventory",
            ],
        },
    }
}
