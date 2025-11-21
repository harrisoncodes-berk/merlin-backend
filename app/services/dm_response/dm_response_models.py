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
    # update_inventory: UpdateInventory | None = None
    # update_health: UpdateHealth | None = None


# OUTPUT_SCHEMA = {
#     "format": {
#         "type": "json_schema",
#         "name": "DMResponse",
#         "strict": True,
#         "schema": {
#             "properties": {
#                 "message_to_user": {"title": "Message To User", "type": "string"},
#                 "update_adventure_status": {
#                     "properties": {
#                         "summary": {"title": "Summary", "type": "string"},
#                         "location": {"title": "Location", "type": "string"},
#                         "combat_state": {"title": "Combat State", "type": "boolean"},
#                     },
#                     "required": ["summary", "location", "combat_state"],
#                     "title": "UpdateAdventureStatus",
#                     "type": "object",
#                     "additionalProperties": False,
#                 },
#             },
#             "required": ["message_to_user"],
#             "title": "DMResponse",
#             "type": "object",
#             "additionalProperties": False,
#         },
#     }
# }