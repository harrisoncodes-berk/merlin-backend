import os
from openai import AsyncOpenAI

class NewOpenAIGateway:
    def __init__(self, model: str, api_key: str):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str):
        resp = await self._client.responses.create(
            model=self._model,
            input=prompt
        )
        return resp

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

gateway = NewOpenAIGateway(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

print(gateway.generate("Hello, how are you?"))