from __future__ import annotations
from typing import Any, List, Optional
import asyncio

from openai import OpenAI, AsyncOpenAI

from .base import LLMClient
from .types import (
    PromptStack,
    ToolSpec,
    LLMResult,
    LLMChunk,
    Usage,
    PromptPart,
)


def _normalize_role(role: str | None) -> str:
    r = (role or "").lower()
    if r in ("assistant", "system", "user", "tool"):
        return r
    if r in ("ai", "dm", "bot"):
        return "assistant"
    return "user"


def _stack_to_chat_messages(stack: PromptStack) -> List[dict[str, str]]:
    msgs: List[dict[str, str]] = []

    def sys(parts: list[PromptPart] | None):
        if not parts:
            return
        for p in parts:
            if p.content:
                msgs.append({"role": "system", "content": p.content})

    sys(stack.system)
    sys(stack.developer)
    sys(stack.session_summary)
    sys(stack.retrieval_chunks)
    sys(stack.scratchpads)

    for p in stack.recent_turns:
        if not p.content:
            continue
        msgs.append({"role": _normalize_role(p.role), "content": p.content})

    assert any(m["role"] in ("user", "system") for m in msgs), (
        "Prompt missing user/system message"
    )
    return msgs


class OpenAILLM(LLMClient):
    """
    A flexible OpenAI adapter that automatically routes:
      - Chat Completions API → for GPT-4o, GPT-4o-mini, GPT-5 (chat)
      - Responses API → for reasoning models (o4, o4-mini, o3, etc.)
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        default_timeout_s: int = 30,
        max_retries: int = 3,
        backoff_ms: int = 250,
        enable_tools: bool = False,
    ):
        self._model = model
        self._timeout = default_timeout_s
        self._max_retries = max_retries
        self._backoff_ms = backoff_ms
        self._enable_tools = enable_tools

        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)

    def name(self) -> str:
        return "openai"

    def model(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        prompt_stack: PromptStack,
        tools: Optional[List[ToolSpec]],
        temperature: float,
        max_output_tokens: int,
        json_mode: bool,
        timeout_s: int,
        trace_id: Optional[str],
    ) -> LLMResult:
        if self._is_reasoning_model(self._model):
            return await self._generate_with_responses_api(
                prompt_stack, temperature, max_output_tokens, json_mode, timeout_s
            )
        else:
            return await self._generate_with_chat_api(
                prompt_stack, temperature, max_output_tokens, json_mode, timeout_s
            )

    async def stream(
        self,
        *,
        prompt_stack: PromptStack,
        tools: Optional[List[ToolSpec]],
        temperature: float,
        max_output_tokens: int,
        json_mode: bool,
        timeout_s: int,
        trace_id: Optional[str],
    ):
        # Placeholder: call non-stream generate for now
        result = await self.generate(
            prompt_stack=prompt_stack,
            tools=tools,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            json_mode=json_mode,
            timeout_s=timeout_s,
            trace_id=trace_id,
        )
        yield LLMChunk(delta=result.text, is_final=True, usage=result.usage)

    async def _generate_with_chat_api(
        self,
        prompt_stack: PromptStack,
        temperature: float,
        max_output_tokens: int,
        json_mode: bool,
        timeout_s: int,
    ) -> LLMResult:
        messages = _stack_to_chat_messages(prompt_stack)

        def _call():
            kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "temperature": float(temperature),
                "max_tokens": int(max_output_tokens),
            }
            if json_mode and any(p in self._model for p in ("gpt-4o", "gpt-5")):
                kwargs["response_format"] = {"type": "json_object"}
            return self._client.chat.completions.create(**kwargs)

        resp = await asyncio.wait_for(asyncio.to_thread(_call), timeout=timeout_s)
        choice = resp.choices[0]
        text = (choice.message.content or "").strip()

        usage = (
            Usage(
                prompt_tokens=resp.usage.prompt_tokens,
                completion_tokens=resp.usage.completion_tokens,
                total_tokens=resp.usage.total_tokens,
            )
            if getattr(resp, "usage", None)
            else None
        )

        return LLMResult(
            text=text,
            tool_calls=[],
            usage=usage,
            finish_reason=choice.finish_reason,
            raw={"id": resp.id, "model": resp.model},
        )

    async def _generate_with_responses_api(
        self,
        prompt_stack: PromptStack,
        temperature: float,
        max_output_tokens: int,
        json_mode: bool,
        timeout_s: int,
    ) -> LLMResult:
        """
        For reasoning models (e.g., o4, o4-mini, future gpt-5-reasoning)
        Uses the newer Responses API.
        """
        text_input = self._stack_to_transcript(prompt_stack)
        params: dict[str, Any] = {
            "model": self._model,
            "input": text_input,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        if json_mode:
            params["response_format"] = {"type": "json_object"}

        resp = await self._async_client.responses.create(**params, timeout=timeout_s)
        text = getattr(resp, "output_text", None) or ""
        if not text and hasattr(resp, "output"):
            for item in reversed(resp.output):
                if getattr(item, "type", None) == "message" and item.content:
                    for part in item.content:
                        if getattr(part, "type", None) == "output_text":
                            text += part.text or ""

        usage = (
            Usage(
                prompt_tokens=resp.usage.prompt_tokens,
                completion_tokens=resp.usage.completion_tokens,
                total_tokens=resp.usage.total_tokens,
            )
            if getattr(resp, "usage", None)
            else None
        )

        return LLMResult(
            text=text.strip(),
            tool_calls=[],
            usage=usage,
            finish_reason="stop",
            raw={"id": resp.id, "model": resp.model},
        )

    def _stack_to_transcript(self, stack: PromptStack) -> str:
        """Flatten chat stack to a readable transcript for Responses API."""
        lines = []
        for p in stack.recent_turns:
            if not p.content:
                continue
            lines.append(f"{_normalize_role(p.role).upper()}: {p.content}")
        return "\n".join(lines)

    def _is_reasoning_model(self, model: str) -> bool:
        """Detect reasoning-type models that require Responses API."""
        return model.lower().startswith(("o4", "o3")) or "reasoning" in model.lower()
