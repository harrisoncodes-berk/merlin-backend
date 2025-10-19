from typing import Any, List
import asyncio

from openai import OpenAI, AsyncOpenAI

from .base import LLMClient
from .types import PromptPayload, LLMResult


def _is_reasoning_model(model: str) -> bool:
    m = model.lower()
    return m.startswith(("o4", "o3")) or "reasoning" in m


def _to_chat_messages(payload: PromptPayload) -> List[dict]:
    msgs: List[dict] = []
    for s in payload.system_messages:
        if s:
            msgs.append({"role": "system", "content": s})
    for u in payload.user_messages:
        if u:
            msgs.append({"role": "user", "content": u})
    assert any(m["role"] == "user" for m in msgs), (
        "At least one user message is required"
    )
    return msgs


def _to_transcript(payload: PromptPayload) -> str:
    lines: List[str] = []
    for s in payload.system_messages:
        if s:
            lines.append(f"SYSTEM: {s}")
    for u in payload.user_messages:
        if u:
            lines.append(f"USER: {u}")
    return "\n".join(lines)


class OpenAILLM(LLMClient):
    """
    Dual-path adapter:
      - Chat Completions for non-reasoning models (gpt-4o, gpt-4o-mini, gpt-5*)
      - Responses API for reasoning models (o4, o4-mini, o3*)
    """

    def __init__(self, api_key: str, model: str, default_timeout_s: int = 30):
        self._model = model
        self._timeout = default_timeout_s
        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)

    def name(self) -> str:
        return "openai"

    def model(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        prompt_payload: PromptPayload,
        temperature: float = 0.7,
        max_tokens: int = 512,
        json_mode: bool = False,
        timeout_s: int = None,
    ) -> LLMResult:
        timeout = timeout_s or self._timeout
        if _is_reasoning_model(self._model):
            return await self._generate_with_responses_api(
                prompt_payload, temperature, max_tokens, json_mode, timeout
            )
        else:
            return await self._generate_with_chat_api(
                prompt_payload, temperature, max_tokens, json_mode, timeout
            )

    async def _generate_with_chat_api(
        self,
        prompt_payload: PromptPayload,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        timeout_s: int,
    ) -> LLMResult:
        messages = _to_chat_messages(prompt_payload)

        def _call():
            kwargs: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            return self._client.chat.completions.create(**kwargs)

        resp = await asyncio.wait_for(asyncio.to_thread(_call), timeout=timeout_s)
        choice = resp.choices[0]
        text = (choice.message.content or "").strip()

        return LLMResult(
            text=text,
            finish_reason=choice.finish_reason,
            raw={"id": resp.id, "model": resp.model},
        )

    async def _generate_with_responses_api(
        self,
        prompt_payload: PromptPayload,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        timeout_s: int,
    ) -> LLMResult:
        input_text = _to_transcript(prompt_payload)

        params: dict[str, Any] = {
            "model": self._model,
            "input": input_text,
            "temperature": float(temperature),
            "max_output_tokens": int(max_tokens),
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

        return LLMResult(
            text=(text or "").strip(),
            finish_reason="stop",
            raw={
                "id": getattr(resp, "id", None),
                "model": getattr(resp, "model", self._model),
            },
        )
