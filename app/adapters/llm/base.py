from typing import Protocol

from app.adapters.llm.types import LLMResult, PromptPayload


class LLMClient(Protocol):
    def name(self) -> str: ...
    def model(self) -> str: ...

    async def generate(
        self,
        *,
        prompt_payload: PromptPayload,
        temperature: float = 0.7,
        max_tokens: int = 512,
        json_mode: bool = False,
        timeout_s: int = 30,
    ) -> LLMResult: ...


class NoOpLLM:
    def __init__(self, model: str = "noop"):
        self._model = model

    def name(self) -> str:
        return "noop"

    def model(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        prompt_payload: PromptPayload,
        temperature: float = 0.7,
        max_tokens: int = 512,
        json_mode: bool = False,
        timeout_s: int = 30,
    ) -> LLMResult:
        return LLMResult(
            text="The corridor smells of damp stone and old secrets. Footsteps echo ahead.",
            finish_reason="stop",
            raw={"provider": "noop"},
        )
