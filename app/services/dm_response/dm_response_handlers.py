from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.character_common import Item
from app.repos.character_repo import CharacterRepo
from app.repos.chat_repo import ChatRepo
from app.services.dm_response.dm_response_models import (
    AddItemToInventory,
    RemoveItemFromInventory,
)


async def update_adventure_status(
    chat_repo: ChatRepo, session_id: str, adventure_status: AdventureStatus
):
    """Updates the adventure status for the given session based on the current turn.

    Args:
        chat_repo: The chat repository to update the adventure status.
        session_id: The session ID to update the adventure status for.
        result_text: The result text from the LLM to update the adventure status from.
    """
    await chat_repo.update_session_adventure_status(session_id, adventure_status)


async def add_item_to_inventory(
    character_repo: CharacterRepo,
    character: Character,
    add_item_to_inventory: AddItemToInventory,
):
    """Adds an item to the character's inventory.

    Args:
        character_repo: The character repository to add the item to the inventory.
        character: The character to add the item to the inventory for.
        add_item_to_inventory: The item to add to the inventory.
    """
    item = Item(
        id=add_item_to_inventory.item_id,
        name=add_item_to_inventory.name,
        quantity=add_item_to_inventory.quantity,
        weight=add_item_to_inventory.weight,
        description=add_item_to_inventory.description,
    )
    updated_inventory = character.inventory + [item]
    await character_repo.update_character_inventory(character.id, updated_inventory)

async def remove_item_from_inventory(
    character_repo: CharacterRepo,
    character: Character,
    remove_item_from_inventory: RemoveItemFromInventory,
):
    """Removes an item from the character's inventory.

    Args:
        character_repo: The character repository to remove the item from the inventory.
        character: The character to remove the item from the inventory for.
        remove_item_from_inventory: The item to remove from the inventory.
    """
    updated_inventory = [item for item in character.inventory if item.id != remove_item_from_inventory.item_id]
    await character_repo.update_character_inventory(character.id, updated_inventory)