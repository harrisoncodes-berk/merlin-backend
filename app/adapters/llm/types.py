from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field


class InputMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class FunctionCall(BaseModel):
    call_id: str
    name: str
    arguments: str
    type: Literal["function_call"] = "function_call"


class FunctionCallOutput(BaseModel):
    call_id: str
    output: str
    type: Literal["function_call_output"] = "function_call_output"


class PromptPayload(BaseModel):
    messages: list[InputMessage | FunctionCall | FunctionCallOutput]


class LLMResult(BaseModel):
    text: str
    finish_reason: Optional[str] = None
    raw: Dict = Field(default_factory=dict)
