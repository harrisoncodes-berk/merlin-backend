from openai import AsyncOpenAI
from openai.types.responses import Response
from pydantic import BaseModel

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
        output_schema: BaseModel = None,
    ) -> Response:
        input_payload = prompt_payload.model_dump_json()
        params = {
            "model": self._model,
            "input": input_payload,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        if tools:
            params["tools"] = tools
        if output_schema:
            params["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": output_schema.__name__,
                    "strict": True,
                    "schema": _base_model_to_json_schema(output_schema),
                },
            }
        print("PARAMS:", params)

        try:
            resp = await self._client.responses.create(**params)
        except Exception as e:
            print(e)
            raise
        return resp


def _base_model_to_json_schema(base_model: BaseModel) -> dict:
    schema = base_model.model_json_schema()

    def _fix(obj: dict) -> None:
        if obj.get("type") == "object":
            if "additionalProperties" not in obj:
                obj["additionalProperties"] = False

            props = obj.get("properties")
            if isinstance(props, dict):
                keys = list(props.keys())
                if keys:
                    obj["required"] = keys

        for v in obj.get("$defs", {}).values():
            if isinstance(v, dict):
                _fix(v)
        for v in obj.get("properties", {}).values():
            if isinstance(v, dict):
                _fix(v)
        items = obj.get("items")
        if isinstance(items, dict):
            _fix(items)

    _fix(schema)
    return schema
