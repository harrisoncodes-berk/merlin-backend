from dataclasses import asdict

from app.domains.chat import Session
from app.repos.adventure_repo import AdventureRepo
from app.repos.chat_repo import ChatRepo


class SessionService:
    """Service for managing chat sessions."""

    def __init__(self, adventure_repo: AdventureRepo, chat_repo: ChatRepo):
        self.adventure_repo = adventure_repo
        self.chat_repo = chat_repo

    async def get_or_create_active_session(
        self, user_id: str, character_id: str
    ) -> Session:
        """Get or create an active session for a user and character."""
        existing_session = await self.chat_repo.get_session_for_character(
            user_id, character_id
        )
        if existing_session and not existing_session.archived_at:
            return existing_session

        new_adventure = (await self.adventure_repo.list_adventures())[0]

        new_session = await self.chat_repo.create_session(
            user_id,
            character_id,
            new_adventure.title,
            new_adventure.story_brief,
            asdict(new_adventure.starting_status),
        )

        await self.chat_repo.db_session.commit()
        
        return new_session
