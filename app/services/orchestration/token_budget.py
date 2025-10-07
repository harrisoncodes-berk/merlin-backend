from typing import Tuple, Dict
from app.adapters.llm.types import PromptStack


def estimate_tokens(prompt_stack: PromptStack, model: str) -> int:
    total_chars = 0
    for section in [
        prompt_stack.system,
        prompt_stack.developer,
        prompt_stack.session_summary,
        prompt_stack.retrieval_chunks,
        prompt_stack.recent_turns,
        prompt_stack.scratchpads,
    ]:
        total_chars += sum(len(p.content) for p in section)
    return max(1, total_chars // 4)


def apply_budget(
    prompt_stack: PromptStack, *, soft_limit: int, hard_limit: int
) -> Tuple[PromptStack, Dict]:
    est = estimate_tokens(prompt_stack, model="unknown")
    if est <= soft_limit:
        return prompt_stack, {
            "applied": False,
            "strategy": "none",
            "estimate_tokens": est,
        }

    pruned = PromptStack(**prompt_stack.model_dump())
    while pruned.recent_turns and estimate_tokens(pruned, model="unknown") > soft_limit:
        pruned.recent_turns = pruned.recent_turns[1:]  # drop oldest
    strategy = (
        "drop_oldest"
        if pruned.recent_turns != prompt_stack.recent_turns
        else "truncate"
    )

    return pruned, {
        "applied": True,
        "strategy": strategy,
        "estimate_tokens": estimate_tokens(pruned, "unknown"),
    }
