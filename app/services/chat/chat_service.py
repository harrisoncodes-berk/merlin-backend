import json
import time
from typing import Optional, Tuple
from dataclasses import asdict

from app.adapters.llm.base import LLMClient
from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.chat import Session
from app.adapters.llm.types import PromptPayload
from app.services.orchestration.prompt_builder import PromptBuilder
from app.services.orchestration import token_budget
from app.services.observability.logging import log_event
from app.services.reliability.circuit_breaker import CircuitBreaker
from app.settings import get_settings
from app.repos.adventure_repo import AdventureRepo
from app.repos.character_repo import CharacterRepo
from app.repos.chat_repo import ChatRepo


class ChatService:
    """
    Orchestrates one chat turn (non-streaming):
      - persist user message
      - build prompt payload and apply token budget
      - check circuit breaker
      - call LLM.generate(...)
      - persist assistant message
      - return the inserted assistant Message (with createdAt)
    """

    def __init__(
        self,
        *,
        llm: LLMClient,
        adventure_repo: AdventureRepo,
        character_repo: CharacterRepo,
        chat_repo: ChatRepo,
        circuit: CircuitBreaker | None = None,
    ):
        self.llm = llm
        self.adventure_repo = adventure_repo
        self.character_repo = character_repo
        self.chat_repo = chat_repo
        self.circuit = circuit or CircuitBreaker(open_threshold=5, reset_seconds=60)
        self.settings = get_settings()

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
            asdict(new_adventure.starting_status),
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
        trace_id: Optional[str] = None,
    ):
        """
        Persists the user turn, builds and budgets the prompt payload,
        consults the circuit breaker, invokes the LLM, persists the assistant turn,
        and returns the created assistant message row.
        """
        await self.chat_repo.insert_user_message_row(session_id, user_text)

        character, session = await self._load_context(user_id, session_id)

        prompt_payload = self._build_prompt_payload(session, character, user_text)

        pruned_prompt_payload, budget_meta = self._apply_budget(prompt_payload)

        if self.circuit.is_open():
            return await self._respond_cooldown(
                session_id, user_id, trace_id, budget_meta
            )

        self._log_start(user_id, session_id, trace_id, budget_meta)

        t0 = time.time()
        try:
            result_text = await self._call_llm(pruned_prompt_payload)

            assistant_text = self._extract_message_to_user(result_text)
            msg = await self.chat_repo.insert_assistant_message_row(session_id, assistant_text)

            await self._update_adventure_status(session_id, result_text)

            await self.chat_repo.db_session.commit()

            self.circuit.record_success()
            self._log_end(user_id, session_id, trace_id, t0, budget_meta)
            
            return msg
        except Exception as e:
            self.circuit.record_failure()
            self._log_error(user_id, session_id, trace_id, budget_meta, e)
            raise

    async def _load_context(
        self, user_id: str, session_id: str
    ) -> Tuple[Character, Session]:
        session = await self.chat_repo.get_session(user_id, session_id)
        character = await self.character_repo.get_character_by_session_id(
            user_id, session_id
        )
        return character, session

    def _build_prompt_payload(
        self, session: Session, character: Character, user_text: str
    ) -> PromptPayload:
        builder = PromptBuilder()
        return builder.build_standard_prompt(
            story_brief=session.story_brief,
            adventure_status=session.adventure_status,
            user_message=user_text,
            character=character,
        )

    def _apply_budget(self, payload):
        pruned_payload, budget_meta = token_budget.apply_budget(
            payload,
            soft_limit=self.settings.llm_soft_prompt_budget,
            hard_limit=self.settings.llm_hard_prompt_budget,
        )
        return pruned_payload, budget_meta

    async def _respond_cooldown(
        self, session_id: str, user_id: str, trace_id: Optional[str], budget_meta
    ):
        cooldown = self.circuit.remaining_cooldown()
        assistant_text = f"The DM is catching their breath (cooldown {cooldown}s)."
        msg = await self.chat_repo.insert_assistant_message_row(
            session_id, assistant_text
        )
        await self.chat_repo.db_session.commit()
        log_event(
            "llm.call.end",
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
            provider="circuit-open",
            model="n/a",
            streaming=False,
            latency_ms=0,
            usage=None,
            tool_calls=[],
            retry_count=0,
            circuit_state="open",
            budgeting=budget_meta,
        )
        return msg

    def _log_start(
        self, user_id: str, session_id: str, trace_id: Optional[str], budget_meta
    ):
        log_event(
            "llm.call.start",
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
            provider=self.llm.name(),
            model=self.llm.model(),
            streaming=False,
            budgeting=budget_meta,
            circuit_state="closed",
        )

    def _log_end(
        self,
        user_id: str,
        session_id: str,
        trace_id: Optional[str],
        t0: float,
        budget_meta,
    ):
        log_event(
            "llm.call.end",
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
            provider=self.llm.name(),
            model=self.llm.model(),
            streaming=False,
            latency_ms=int((time.time() - t0) * 1000),
            usage=None,
            tool_calls=[],
            retry_count=0,
            circuit_state="closed",
            budgeting=budget_meta,
        )

    def _log_error(
        self,
        user_id: str,
        session_id: str,
        trace_id: Optional[str],
        budget_meta,
        e: Exception,
    ):
        log_event(
            "llm.call.error",
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
            provider=self.llm.name(),
            model=self.llm.model(),
            streaming=False,
            error={"type": type(e).__name__, "message_redacted": "generation failed"},
            circuit_state="open" if self.circuit.is_open() else "closed",
            budgeting=budget_meta,
        )

    async def _call_llm(self, pruned_payload):
        result = await self.llm.generate(
            prompt_payload=pruned_payload,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_output_tokens,
            json_mode=self.settings.llm_json_mode,
            timeout_s=self.settings.llm_timeout_seconds,
        )
        return result.text

    def _extract_message_to_user(self, result_text: str) -> str:
        """
        Parses the model output and extracts message_to_user, with a safe fallback.
        """
        try:
            data = json.loads(result_text)
            mt = data.get("message_to_user")
            if isinstance(mt, str) and mt.strip():
                return mt.strip()
        except Exception:
            pass
        return result_text

    async def _update_adventure_status(self, session_id: str, result_text: str):
        adventure_status = json.loads(result_text).get("adventure_status")
        await self.chat_repo.update_session_adventure_status(
            session_id, AdventureStatus(**adventure_status)
        )
