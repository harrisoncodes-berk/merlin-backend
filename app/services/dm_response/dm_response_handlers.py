from app.domains.adventures import AdventureStatus
from app.repos.chat_repo import ChatRepo


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
