from typing import Tuple, Dict
from app.adapters.llm.types import PromptPayload


def estimate_tokens(payload: PromptPayload, model: str = "unknown") -> int:
    """
    Very rough character-to-token estimate for budgeting.
    """
    total_chars = 0
    total_chars += sum(len(s or "") for s in payload.system_messages)
    total_chars += sum(len(u or "") for u in payload.user_messages)
    return max(1, total_chars // 4)


def _shrink_text_to_ratio(text: str, ratio: float) -> str:
    """
    Returns a prefix of text scaled by ratio, bounded to at least 1 char if text is non-empty.
    """
    if not text:
        return text
    n = max(1, int(len(text) * ratio))
    return text[:n]


def apply_budget(
    payload: PromptPayload,
    *,
    soft_limit: int,
    hard_limit: int,
) -> Tuple[PromptPayload, Dict]:
    """
    Prunes the payload to fit within soft_limit, not to exceed hard_limit.
    Strategy:
      1) Prefer shrinking the conversation user message (index 1) if present.
      2) Then shrink the character sheet (index 0).
      3) As a last resort, shrink the task (last index) and, if still over, hard-truncate all.
    Returns a new PromptPayload and a small budgeting metadata dict.
    """
    est = estimate_tokens(payload)
    if est <= soft_limit:
        return payload, {"applied": False, "strategy": "none", "estimate_tokens": est}

    pruned = PromptPayload(**payload.model_dump())
    strategy_steps = []

    def within(limit: int) -> bool:
        return estimate_tokens(pruned) <= limit

    if len(pruned.user_messages) >= 2 and pruned.user_messages[1]:
        original = pruned.user_messages[1]
        for r in (0.75, 0.5, 0.35, 0.25):
            pruned.user_messages[1] = _shrink_text_to_ratio(original, r)
            strategy_steps.append(f"shrink_conversation_{int(r * 100)}")
            if within(soft_limit):
                return pruned, {
                    "applied": True,
                    "strategy": strategy_steps,
                    "estimate_tokens": estimate_tokens(pruned),
                }

    if len(pruned.user_messages) >= 1 and pruned.user_messages[0]:
        original = pruned.user_messages[0]
        for r in (0.75, 0.5, 0.35, 0.25):
            pruned.user_messages[0] = _shrink_text_to_ratio(original, r)
            strategy_steps.append(f"shrink_character_{int(r * 100)}")
            if within(soft_limit):
                return pruned, {
                    "applied": True,
                    "strategy": strategy_steps,
                    "estimate_tokens": estimate_tokens(pruned),
                }

    if len(pruned.user_messages) >= 1:
        idx = len(pruned.user_messages) - 1
        original = pruned.user_messages[idx]
        for r in (0.75, 0.5, 0.35, 0.25):
            pruned.user_messages[idx] = _shrink_text_to_ratio(original, r)
            strategy_steps.append(f"shrink_task_{int(r * 100)}")
            if within(soft_limit):
                return pruned, {
                    "applied": True,
                    "strategy": strategy_steps,
                    "estimate_tokens": estimate_tokens(pruned),
                }

    if estimate_tokens(pruned) > hard_limit:
        budget_chars = hard_limit * 4
        sys_join = "\n".join(pruned.system_messages)
        usr_join = "\n".join(pruned.user_messages)
        combined = (sys_join + "\n" + usr_join).strip()
        combined = combined[:budget_chars]
        midpoint = min(len(sys_join), len(combined))
        new_sys = sys_join[:midpoint]
        new_usr = combined[midpoint:]
        pruned.system_messages = [new_sys] if new_sys else []
        pruned.user_messages = [new_usr] if new_usr else []
        strategy_steps.append("hard_truncate_all")

    return pruned, {
        "applied": True,
        "strategy": strategy_steps or ["no_room_left"],
        "estimate_tokens": estimate_tokens(pruned),
    }
