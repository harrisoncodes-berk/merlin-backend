import json
from typing import List, Tuple

from app.adapters.llm.openai_client import OpenAILLM
from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.chat import Message, Session
from app.adapters.llm.types import PromptPayload
from app.services.orchestration.prompt_builder import PromptBuilder
from app.repos.adventure_repo import AdventureRepo
from app.repos.character_repo import CharacterRepo
from app.repos.chat_repo import ChatRepo


class ChatService:
    """Handles the chat service for the given user and session."""

    def __init__(
        self,
        llm: OpenAILLM,
        adventure_repo: AdventureRepo,
        character_repo: CharacterRepo,
        chat_repo: ChatRepo,
    ):
        self.llm = llm
        self.adventure_repo = adventure_repo
        self.character_repo = character_repo
        self.chat_repo = chat_repo

    def build_initial_message(
        self,
        character_name: str,
        adventure_title: str,
        story_brief: str,
        starting_status: str,
    ) -> str:
        return f"""Greetings, {character_name}! Welcome to {adventure_title}! {story_brief} {starting_status} How do you proceed, adventurer?"""

    async def initialize_session(self, user_id: str, character_id: str) -> Session:
        """
        Returns an existing active session for the character if available,
        otherwise creates a new session, seeds the opening assistant message,
        and commits it.
        """

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
            new_adventure.starting_status,
        )

        character = await self.character_repo.get_character_by_character_id(
            user_id, character_id
        )

        first_message = self.build_initial_message(
            character_name=character.name,
            adventure_title=new_session.adventure_title,
            story_brief=new_session.story_brief,
            starting_status=new_session.adventure_status.summary,
        )
        _ = await self.chat_repo.insert_assistant_message_row(
            new_session.session_id, first_message
        )

        await self.chat_repo.db_session.commit()

        return new_session

    async def handle_turn(
        self,
        *,
        user_id: str,
        session_id: str,
        user_text: str,
    ):
        """Handles a single turn of the chat."""
        await self.chat_repo.insert_user_message_row(session_id, user_text)

        session, chat_history, character = await self._load_context(user_id, session_id)

        prompt_payload = self._build_prompt_payload(session, chat_history, character, user_text)

        try:
            result_text = await self._call_llm(prompt_payload)

            assistant_text = self._extract_message_to_user(result_text)
            msg = await self.chat_repo.insert_assistant_message_row(session_id, assistant_text)

            await self._update_adventure_status(session_id, result_text)

            await self.chat_repo.db_session.commit()
            
            return msg
        except Exception as e:
            print(e)
            raise

    async def _load_context(
        self, user_id: str, session_id: str
    ) -> Tuple[Session, List[Message], Character]:
        """Loads the session, chat history, and character for the given user and session."""

        session = await self.chat_repo.get_session(user_id, session_id)
        chat_history = await self.chat_repo.list_messages(session_id, limit=10)
        character = await self.character_repo.get_character_by_session_id(
            user_id, session_id
        )
        return session, chat_history, character

    def _build_prompt_payload(
        self, session: Session, chat_history: List[Message], character: Character, user_text: str
    ) -> PromptPayload:
        """Builds the prompt payload for the given session, chat history, character, and user text."""
        builder = PromptBuilder()
        return builder.build_standard_prompt(
            story_brief=session.story_brief,
            adventure_status=session.adventure_status,
            chat_history=chat_history,
            user_message=user_text,
            character=character,
        )

    async def _call_llm(self, pruned_payload):
        result = await self.llm.generate(
            prompt_payload=pruned_payload,
            temperature=0.7,
            max_tokens=700,
            json_mode=True,
        )
        return result.text

    def _extract_message_to_user(self, result_text: str) -> str:
        """Parses the model output and extracts message_to_user, with a safe fallback."""
        try:
            data = json.loads(result_text)
            mt = data.get("message_to_user")
            if isinstance(mt, str) and mt.strip():
                return mt.strip()
        except Exception:
            pass
        return result_text

    async def _update_adventure_status(self, session_id: str, result_text: str):
        """Updates the adventure status for the given session based on the model output."""
        adventure_status = json.loads(result_text).get("adventure_status")
        await self.chat_repo.update_session_adventure_status(
            session_id, AdventureStatus(**adventure_status)
        )
