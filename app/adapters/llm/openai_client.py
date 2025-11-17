from openai import AsyncOpenAI
from openai.types.responses import Response

from app.adapters.llm.types import PromptPayload


class OpenAILLM:
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
        tools: list[dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        json_mode: bool = False,
    ) -> Response:
        input_payload = self._payload_to_input(prompt_payload)
        params = {
            "model": self._model,
            "input": input_payload,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if tools:
            params["tools"] = tools
        if json_mode:
            params["text"] = {"format": {"type": "json_object"}}

        try:
            resp = await self._client.responses.create(**params)
        except Exception as e:
            print(e)
            raise
        return resp

    def _payload_to_input(self, prompt_payload: PromptPayload) -> list[dict]:
        return [
            _format_input_msg("system", s) for s in prompt_payload.system_messages
        ] + [_format_input_msg("user", u) for u in prompt_payload.user_messages]


def _format_input_msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}
