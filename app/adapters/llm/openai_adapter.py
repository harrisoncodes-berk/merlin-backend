from typing import AsyncIterator, List, Optional
from .base import LLMClient
from .types import PromptStack, ToolSpec, LLMResult, LLMChunk


class OpenAILLM(LLMClient):
    """
    Phase 0 stub — compiles, but not calling OpenAI yet.
    In Phase 1 you'll implement generate/stream using the OpenAI SDK.
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
        self._api_key = api_key
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
        # TEMP: same behavior as NoOp until Phase 1.
        return LLMResult(
            text="(OpenAI adapter stub) The corridor smells of damp stone and old secrets. Footsteps echo ahead.",
            usage=None,
            raw={"provider": "openai-stub"},
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
        yield LLMChunk(
            delta="(OpenAI adapter stub) The corridor smells of damp stone and old secrets. Footsteps echo ahead.",
            is_final=True,
        )
