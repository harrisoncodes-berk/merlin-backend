import json
from typing import List, Tuple
from openai.types.responses import Response

from app.adapters.llm.openai_client import OpenAILLM
from app.domains.character import Character
from app.domains.adventures import AdventureStatus
from app.domains.chat import Message, Session
from app.adapters.llm.types import PromptPayload
from app.services.orchestration.prompt_builder import PromptBuilder
from app.repos.adventure_repo import AdventureRepo
from app.repos.character_repo import CharacterRepo
from app.repos.chat_repo import ChatRepo
from app.services.dm_response.dm_response_handlers import (
    add_items_to_inventory,
    remove_items_from_inventory,
    update_adventure_status,
)
from app.services.dm_response.dm_response_models import DMResponse, DM_RESPONSE_SCHEMA
from app.services.tools.tools import ability_check
from app.services.tools.tools_mapping import TOOLS_FOR_LLM


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
        """Handles chat turn for a new session."""

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
        user_id: str,
        session_id: str,
        user_text: str,
    ):
        """Handles a single turn of the chat."""
        await self.chat_repo.insert_user_message_row(session_id, user_text)

        session, chat_history, character = await self._load_context(user_id, session_id)

        prompt_builder = PromptBuilder(
            story_brief=session.story_brief,
            character=character,
            adventure_status=session.adventure_status,
            chat_history=chat_history,
        )
        prompt_payload = prompt_builder.prompt_payload

        try:
            response = await self._call_llm(prompt_payload, tools=TOOLS_FOR_LLM)

            for item in response.output:
                if item.type == "function_call":
                    if item.name == "ability_check":
                        args = json.loads(item.arguments)
                        call_id = item.call_id
                        output = ability_check(character, **json.loads(item.arguments))
                        prompt_builder.add_function_call_messages(
                            call_id=call_id,
                            name=item.name,
                            arguments=args,
                            output=output,
                        )

            follow_up_prompt = prompt_builder.prompt_payload

            follow_up_response = await self._call_llm(
                follow_up_prompt, output_schema=DM_RESPONSE_SCHEMA
            )

            msg = await self._handle_dm_response(
                follow_up_response.output_text, character, session_id
            )

            await self.chat_repo.db_session.commit()

            return msg
        except Exception as e:
            print(e)
            await self.chat_repo.db_session.rollback()
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

    async def _call_llm(
        self,
        pruned_payload: PromptPayload,
        tools: list[dict] = None,
        output_schema: dict = None,
    ) -> Response:
        result = await self.llm.generate(
            prompt_payload=pruned_payload,
            tools=tools,
            output_schema=output_schema,
            temperature=0.7,
            max_tokens=700,
        )
        return result

    async def _handle_dm_response(
        self, dm_response_str: str, character: Character, session_id: str
    ) -> str:
        """Handles the DM response by inserting the message to user and updating the adventure status."""
        dm_response = DMResponse.model_validate_json(dm_response_str)

        message_to_user = dm_response.message_to_user
        msg = await self.chat_repo.insert_assistant_message_row(
            session_id, message_to_user
        )

        adventure_status = AdventureStatus(
            summary=dm_response.update_adventure_status.summary,
            location=dm_response.update_adventure_status.location,
            combat_state=dm_response.update_adventure_status.combat_state,
        )
        await update_adventure_status(self.chat_repo, session_id, adventure_status)

        if dm_response.add_items_to_inventory:
            await add_items_to_inventory(
                self.character_repo, character, dm_response.add_items_to_inventory
            )
        if dm_response.remove_items_from_inventory:
            await remove_items_from_inventory(
                self.character_repo, character, dm_response.remove_items_from_inventory
            )

        return msg
