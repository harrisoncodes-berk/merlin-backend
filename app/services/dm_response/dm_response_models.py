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
