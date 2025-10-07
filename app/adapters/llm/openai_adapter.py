from __future__ import annotations
from typing import AsyncIterator, List, Optional, Dict, Any
import asyncio

from .base import LLMClient
from .types import PromptStack, ToolSpec, LLMResult, LLMChunk, Usage, PromptPart

from openai import OpenAI


def _stack_to_messages(stack: PromptStack) -> List[Dict[str, str]]:
    """
    
    """
    msgs: List[Dict[str, str]] = []

    def sys(parts: List[PromptPart]):
        for p in parts:
            if not p.content:
                continue
            msgs.append({"role": "system", "content": p.content})

    sys(stack.system)
    sys(stack.developer)
    sys(stack.session_summary)
    sys(stack.retrieval_chunks)
    sys(stack.scratchpads)

    for p in stack.recent_turns:
        role = p.role if p.role in ("user", "assistant") else "user"
        if p.content:
            msgs.append({"role": role, "content": p.content})

    return msgs


class OpenAILLM(LLMClient):
    """
    Client for the OpenAI API.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        default_timeout_s: int,
        max_retries: int,
        backoff_ms: int,
        enable_tools: bool,
    ):
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._timeout = default_timeout_s
        self._max_retries = max_retries
        self._backoff_ms = backoff_ms
        self._enable_tools = enable_tools

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
        messages = _stack_to_messages(prompt_stack)

        def _call():
            kwargs: Dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "temperature": float(temperature),
                "max_tokens": int(max_output_tokens),
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            return self._client.chat.completions.create(**kwargs)

        resp = await asyncio.wait_for(asyncio.to_thread(_call), timeout=timeout_s)

        choice = resp.choices[0]
        text = (choice.message.content or "").strip()

        usage = None
        if getattr(resp, "usage", None):
            usage = Usage(
                prompt_tokens=int(resp.usage.prompt_tokens),
                completion_tokens=int(resp.usage.completion_tokens),
                total_tokens=int(resp.usage.total_tokens),
            )

        raw = {
            "id": resp.id,
            "model": resp.model,
            "finish_reason": choice.finish_reason,
        }

        return LLMResult(
            text=text,
            tool_calls=[],
            usage=usage,
            finish_reason=choice.finish_reason,
            raw=raw,
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
    ) -> AsyncIterator[LLMChunk]:
        _ = _stack_to_messages(prompt_stack)
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
