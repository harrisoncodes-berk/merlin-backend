import os
import pytest
from pytest import mark

from app.adapters.llm.openai_adapter import OpenAILLM
from app.adapters.llm.types import PromptPayload

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@mark.asyncio
@mark.live_openai
@mark.parametrize("model", ["gpt-4o-mini", "o4-mini"])  # chat path and responses path
async def test_openai_generate_live(model):
    if not OPENAI_API_KEY:
        pytest.skip("Set OPENAI_API_KEY to run live OpenAI tests.")

    llm = OpenAILLM(api_key=OPENAI_API_KEY, model=model, default_timeout_s=20)

    payload = PromptPayload(
        system_messages=["You are concise."],
        user_messages=[
            "Say 'pong' and stop."
        ],  # must include at least one user message
    )

    res = await llm.generate(
        prompt_payload=payload,
        temperature=0.1,
        max_tokens=16,
        json_mode=False,
        timeout_s=20,
    )

    assert isinstance(res.text, str) and len(res.text) > 0
    assert res.finish_reason in (None, "stop")
