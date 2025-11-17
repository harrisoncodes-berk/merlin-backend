from openai import AsyncOpenAI
from openai.types.responses import Response

from app.adapters.llm.base import LLMClient
from app.adapters.llm.types import PromptPayload, LLMResult


class OpenAILLM(LLMClient):
    def __init__(self, api_key: str, model: str):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    def name(self) -> str:
        return "openai"

    def model(self) -> str:
        return self._model

    async def generate(
        self,
        prompt_payload: PromptPayload,
        temperature: float = 0.7,
        max_tokens: int = 512,
        json_mode: bool = False,
        timeout_s: int = 30,
    ) -> LLMResult:
        input_payload = self._payload_to_input(prompt_payload)
        params = {
            "model": self._model,
            "input": input_payload,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if prompt_payload.tools:
            params["tools"] = prompt_payload.tools
        if json_mode:
            params["text"] = {"format": {"type": "json_object"}}

        try:
            resp = await self._client.responses.create(**params)
            print(resp)
        except Exception as e:
            print(e)
            return LLMResult(
                text="An error occurred while generating the response.",
                finish_reason="error",
                raw={
                    "error": str(e),
                },
            )
        return LLMResult(
            text=getattr(resp, "output_text", None) or "no output text",
        )

    def _payload_to_input(self, prompt_payload: PromptPayload) -> list[dict]:
        return [
            _format_input_msg("system", s) for s in prompt_payload.system_messages
        ] + [_format_input_msg("user", u) for u in prompt_payload.user_messages]


def _format_input_msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}
