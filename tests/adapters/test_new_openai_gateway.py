import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class PromptPayload(BaseModel):
    system_messages: list[dict]
    user_messages: list[dict]
    tools: list[dict] | None = None


class NewOpenAIGateway:
    def __init__(self, model: str, api_key: str):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt_payload: PromptPayload):
        input_payload = self._payload_to_input(prompt_payload)
        params = {
            "model": self._model,
            "input": input_payload,
        }
        if prompt_payload.tools:
            params["tools"] = prompt_payload.tools

        resp = await self._client.responses.create(**params)
        return resp

    def _payload_to_input(self, prompt_payload: PromptPayload) -> list[dict]:
        return prompt_payload.system_messages + prompt_payload.user_messages


def glaze_tool(name: str) -> str:
    return f"{name} is awesome"


async def main():
    gateway = NewOpenAIGateway(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

    tools = [
        {
            "type": "function",
            "name": "glaze_tool",
            "description": "If the prompt describes someone who is awesome, return the name of the person.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                },
                "additionalProperties": False,
                "required": ["name"],
            },
        },
    ]

    test_payload = PromptPayload(
        system_messages=[{"role": "system", "content": "Your job is to determine if the described person is awesome. If so, use the glaze_tool to return the name of the person."}],
        user_messages=[{"role": "user", "content": "Hary did a sick skateboard trick yesterday."}],
        tools=tools,
    )

    response = await gateway.generate(test_payload)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
