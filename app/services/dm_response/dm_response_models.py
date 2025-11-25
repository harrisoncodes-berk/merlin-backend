from pydantic import BaseModel

from app.schemas.character_common import ItemOut


class UpdateAdventureStatus(BaseModel):
    summary: str
    location: str
    combat_state: bool


class AddItemsToInventory(BaseModel):
    items: list[ItemOut]


class RemoveItemsFromInventory(BaseModel):
    items: list[dict]


class UpdateHealth(BaseModel):
    hp_current: int
    hp_max: int


class DMResponse(BaseModel):
    message_to_user: str
    update_adventure_status: UpdateAdventureStatus
    add_items_to_inventory: AddItemsToInventory | None = None
    remove_items_from_inventory: RemoveItemsFromInventory | None = None
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
                "add_items_to_inventory": {
                    "type": ["object", "null"],
                    "description": "Use to add an item to the character's inventory when the user gains an item.",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": "The items to add to the inventory.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "The ID of the item to add to the inventory.",
                                    },
                                    "name": {
                                        "type": "string",
                                        "description": "The name of the item to add to the inventory.",
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "The quantity of the item to add to the inventory.",
                                    },
                                    "weight": {
                                        "type": "number",
                                        "description": "The weight of the item to add to the inventory.",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "The description of the item to add to the inventory.",
                                    },
                                },
                                "required": [
                                    "id",
                                    "name",
                                    "quantity",
                                    "weight",
                                    "description",
                                ],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["items"],
                    "additionalProperties": False,
                },
                "remove_items_from_inventory": {
                    "type": ["object", "null"],
                    "description": "Use to remove an item from the character's inventory when the user loses an item.",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": "The items to remove from the inventory.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "The ID of the item to remove from the inventory.",
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "The quantity of the item to remove from the inventory.",
                                    },
                                },
                                "required": ["id", "quantity"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["items"],
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
            "required": [
                "message_to_user",
                "update_adventure_status",
                "add_items_to_inventory",
                "remove_items_from_inventory",
            ],
        },
    }
}
