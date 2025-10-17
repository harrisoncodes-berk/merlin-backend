from typing import List, Optional

from app.adapters.llm.base import LLMClient
from app.adapters.llm.types import PromptPart, PromptStack
from app.services.orchestration import prompt_builder, token_budget
from app.services.observability.logging import log_event
from app.services.reliability.circuit_breaker import CircuitBreaker
from app.settings import get_settings
from app.repos.chat_repo import ChatRepo


class TurnService:
    """
    Orchestrates one chat turn (non-streaming):
      - persist user message
      - build prompt stack + apply token budget
      - check circuit breaker
      - call LLM.generate(...)
      - persist assistant message
      - return the inserted assistant Message (with createdAt)
    """

    def __init__(
        self, *, llm: LLMClient, repo: ChatRepo, circuit: CircuitBreaker | None = None
    ):
        self.llm = llm
        self.repo = repo
        self.circuit = circuit or CircuitBreaker(open_threshold=5, reset_seconds=60)
        self.settings = get_settings()

    async def handle_turn(
        self,
        *,
        user_id: str,
        session_id: str,
        user_text: str,
        trace_id: Optional[str] = None,
    ):
        _ = await self.repo.insert_user_message_row(session_id, user_text)

        last_msgs = await self.repo.list_messages(session_id, after=None, limit=10)
        recent_parts: List[PromptPart] = [
            PromptPart(role=m.role, content=m.content) for m in last_msgs
        ]

        stack: PromptStack = prompt_builder.build_prompt_stack(
            character_sheet=None,
            session_summary=None,
            retrieved_chunks=[],
            recent_turns=recent_parts,
            scratchpads={},
        )

        pruned_stack, budget_meta = token_budget.apply_budget(
            stack,
            soft_limit=self.settings.llm_soft_prompt_budget,
            hard_limit=self.settings.llm_hard_prompt_budget,
        )

        if self.circuit.is_open():
            cooldown = self.circuit.remaining_cooldown()
            assistant_text = f"The DM is catching their breath (cooldown {cooldown}s)."
            msg = await self.repo.insert_assistant_message_row(
                session_id, assistant_text
            )
            await self.repo.db_session.commit()
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

        try:
            result = await self.llm.generate(
                prompt_stack=pruned_stack,
                tools=None,
                temperature=self.settings.llm_temperature,
                max_output_tokens=self.settings.llm_max_output_tokens,
                json_mode=self.settings.llm_json_mode,
                timeout_s=self.settings.llm_timeout_seconds,
                trace_id=trace_id,
            )
            assistant_text = result.text
            msg = await self.repo.insert_assistant_message_row(
                session_id, assistant_text
            )
            await self.repo.db_session.commit()

            log_event(
                "llm.call.end",
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
                provider=self.llm.name(),
                model=self.llm.model(),
                streaming=False,
                latency_ms=None,
                usage=(result.usage.model_dump() if result.usage else None),
                tool_calls=[tc.model_dump() for tc in result.tool_calls]
                if result.tool_calls
                else [],
                retry_count=0,
                circuit_state="closed",
                budgeting=budget_meta,
            )
            return msg

        except Exception as e:
            self.circuit.record_failure()
            log_event(
                "llm.call.error",
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
                provider=self.llm.name(),
                model=self.llm.model(),
                streaming=False,
                error={
                    "type": type(e).__name__,
                    "message_redacted": "generation failed",
                },
                circuit_state="open" if self.circuit.is_open() else "closed",
                budgeting=budget_meta,
            )
            raise
