from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.character_common import Item
from app.repos.character_repo import CharacterRepo
from app.repos.chat_repo import ChatRepo
from app.services.dm_response.dm_response_models import (
    AddItemsToInventory,
    RemoveItemsFromInventory,
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


async def add_items_to_inventory(
    character_repo: CharacterRepo,
    character: Character,
    add_items_to_inventory: AddItemsToInventory,
):
    """Adds items to the character's inventory.

    Args:
        character_repo: The character repository to add the items to the inventory.
        character: The character to add the items to the inventory for.
        add_items_to_inventory: The items to add to the inventory.
    """
    items = [
        Item(
            id=item.id,
            name=item.name,
            quantity=item.quantity,
            weight=item.weight,
            description=item.description,
        )
        for item in add_items_to_inventory.items
    ]
    updated_inventory = character.inventory + items
    await character_repo.update_character_inventory(character.id, updated_inventory)


async def remove_items_from_inventory(
    character_repo: CharacterRepo,
    character: Character,
    remove_items_from_inventory: RemoveItemsFromInventory,
):
    """Removes items from the character's inventory.

    Args:
        character_repo: The character repository to remove the items from the inventory.
        character: The character to remove the items from the inventory for.
        remove_items_from_inventory: The items to remove from the inventory.
    """
    updated_inventory = [
        item
        for item in character.inventory
        if item.id not in remove_items_from_inventory.items
    ]
    await character_repo.update_character_inventory(character.id, updated_inventory)
