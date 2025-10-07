from typing import Protocol, AsyncIterator, List, Optional
from .types import PromptStack, ToolSpec, LLMResult, LLMChunk


class LLMClient(Protocol):
    def name(self) -> str: ...
    def model(self) -> str: ...

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
    ) -> LLMResult: ...

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
    ) -> AsyncIterator[LLMChunk]: ...


class NoOpLLM:
    """Safe baseline that returns your existing dummy response. Swap out later."""
    def __init__(self, model: str = "noop"):
        self._model = model

    def name(self) -> str:
        return "noop"

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
        from .types import LLMResult
        return LLMResult(
            text="The corridor smells of damp stone and old secrets. Footsteps echo ahead.",
            usage=None,
            raw={"provider": "noop"},
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
        yield LLMChunk(delta="The corridor smells of damp stone and old secrets. Footsteps echo ahead.", is_final=True)
