
from typing import Literal, Optional, List, Dict
from pydantic import BaseModel


PromptRole = Literal["system", "developer", "user", "assistant", "tool"]


class PromptPart(BaseModel):
    role: PromptRole
    content: str
    name: Optional[str] = None
    meta: Dict = {}


class PromptStack(BaseModel):
    system: List[PromptPart] = []
    developer: List[PromptPart] = []
    session_summary: List[PromptPart] = []
    retrieval_chunks: List[PromptPart] = []
    recent_turns: List[PromptPart] = []
    scratchpads: List[PromptPart] = []


class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: Dict


class ToolCall(BaseModel):
    name: str
    arguments: Dict
    id: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResult(BaseModel):
    text: str
    tool_calls: List[ToolCall] = []
    usage: Optional[Usage] = None
    finish_reason: Optional[str] = None
    raw: Dict = {}


class LLMChunk(BaseModel):
    delta: str = ""
    tool_calls_delta: List[ToolCall] = []
    is_final: bool = False
    usage: Optional[Usage] = None
