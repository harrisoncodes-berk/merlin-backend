from dataclasses import dataclass, field
from typing import Iterable, List, Dict, Optional


# -----------------------------
# Data Transfer Objects (pure)
# -----------------------------

@dataclass(frozen=True)
class RecentTurn:
    user: str
    dm: str


@dataclass(frozen=True)
class Status:
    summary: str
    location: str
    in_combat: bool


@dataclass(frozen=True)
class PromptInput:
    # Fixed system/developer text (keep tiny; injected every call by TurnService)
    system_text: str
    developer_text: Optional[str] = None

    # Dynamic context (short briefs only)
    story_brief: str = ""
    character_block: Optional[str] = None        # preformatted block (e.g., YAML)
    character_brief: Optional[str] = None        # 1-line variant, used if block is None
    status: Optional[Status] = None
    recent_turns: Iterable[RecentTurn] = field(default_factory=list)

    # Player input for this turn
    player_text: str = ""

    # Flags & knobs
    flags: Dict[str, bool] = field(default_factory=dict)  # e.g., {"in_combat": False}
    max_chars: Dict[str, int] = field(default_factory=lambda: {
        "story_brief": 600,
        "character_block": 600,
        "character_brief": 180,
        "status": 280,
        "recent_turn_line": 240,
        "player_text": 800,
    })

    # Optional: attach an output contract (JSON schema or human format text).
    # If provided as a dict, it will be rendered compactly beneath "Output Schema".
    output_contract: Optional[Dict] = None


# -----------------------------
# Utility helpers (pure)
# -----------------------------

def _clip(s: Optional[str], limit: int) -> str:
    if not s:
        return ""
    s = " ".join(s.split())  # squash whitespace
    return s if len(s) <= limit else (s[: max(0, limit - 1)] + "…")


def _render_recent(recent: Iterable[RecentTurn], line_limit: int) -> str:
    lines: List[str] = []
    for rt in recent:
        u = _clip(rt.user, line_limit)
        a = _clip(rt.dm, line_limit)
        lines.append(f"- You: {u}\n- DM: {a}")
    return "\n".join(lines)


def _render_rules(in_combat: bool) -> str:
    # Keep this short; you can expand later or branch by flags.
    base = (
        "GAME RULES (Simplified)\n"
        "- All responses must be valid JSON that matches Output Schema.\n"
        "- Use outcome checks for uncertain actions (1d20 + modifier vs DC).\n"
        "- Never invent dice results; request an outcome_check instead.\n"
        "- Keep narration 2–4 sentences; do not control the player's choices.\n"
    )
    combat = (
        "- While in_combat: narrate brief rounds; attack = d20 + bonus vs AC; apply damage to HP; "
        "do not resolve entire fights in one reply; end combat when hostiles are gone.\n"
    )
    movement = (
        "- On movement between areas, include an 'updates.location' and a concise 'updates.summary'.\n"
    )
    return base + movement + (combat if in_combat else "")


def _render_output_schema(contract: Optional[Dict]) -> str:
    # Human-readable contract for the model. Keep minimal but explicit.
    if not contract:
        # Default schema guidance (matches what we designed)
        return (
            "OUTPUT SCHEMA (JSON):\n"
            "{\n"
            '  "message_to_user": string,                 // DM narration (2–4 sentences; end with a prompt)\n'
            '  "updates": {                               // include only if something changed\n'
            '    "summary": string,                       // short recap of what happened\n'
            '    "in_combat": boolean,                    // optional\n'
            '    "location": string,                      // optional\n'
            '    "found_item": string                     // optional\n'
            "  },\n"
            '  "outcome_check": {                         // include only when a roll is needed\n'
            '    "summary": string,                       // e.g., "Tbitty attempts to climb the wall"\n'
            '    "ability": "strength|dexterity|constitution|intelligence|wisdom|charisma",\n'
            '    "skill": "acrobatics|animalHandling|arcana|athletics|deception|history|insight|intimidation|'
            'investigation|medicine|nature|perception|performance|persuasion|religion|sleightOfHand|stealth|survival",\n'
            '    "difficulty": number                     // 5 (easy) to 20 (very hard)\n'
            "  }\n"
            "}\n"
            "Notes: Include only changed fields. If no roll is needed, omit 'outcome_check'. "
            "If entering combat, set updates.in_combat=true. If location changes, set updates.location."
        )
    # Compact JSON dump without importing json (keep the module pure and lightweight)
    # (You can replace with json.dumps(contract, separators=(',',':')) if you prefer.)
    return "OUTPUT SCHEMA (JSON):\n" + str(contract)


def _render_character(pi: PromptInput) -> str:
    if pi.character_block:
        return _clip(pi.character_block, pi.max_chars["character_block"])
    if pi.character_brief:
        return _clip(pi.character_brief, pi.max_chars["character_brief"])
    return "(No character data provided)"


def _render_status(status: Optional[Status], limit: int) -> str:
    if not status:
        return "(No status provided)"
    summary = _clip(status.summary, limit)
    loc = status.location
    combat = "In combat" if status.in_combat else "Not in combat"
    return f"Summary: {summary}\nLocation: {loc}\nCombat State: {combat}"


# -----------------------------
# Prompt Builder (pure)
# -----------------------------

class PromptBuilder:
    """
    Build the messages array for a Chat Completions call.

    The builder is PURE: no I/O, no DB. Pass fully-formed PromptInput from TurnService.
    """

    def build(self, p: PromptInput) -> List[Dict[str, str]]:
        in_combat = p.flags.get("in_combat", False) or (p.status.in_combat if p.status else False)

        # SYSTEM
        system = self._build_system(p.system_text)

        # DEVELOPER (schema & tool usage policy belong here; user cannot override)
        developer = self._build_developer(p.developer_text, in_combat, p.output_contract)

        # USER (compact bundle)
        user = self._build_user(
            story_brief=_clip(p.story_brief, p.max_chars["story_brief"]),
            character=_render_character(p),
            status=_render_status(p.status, p.max_chars["status"]),
            recent=_render_recent(p.recent_turns, p.max_chars["recent_turn_line"]),
            rules=_render_rules(in_combat),
            player=_clip(p.player_text, p.max_chars["player_text"]),
            output_schema=_render_output_schema(p.output_contract),
        )

        messages: List[Dict[str, str]] = [system]
        if developer:
            messages.append(developer)
        messages.append(user)
        return messages

    # -------- sections (private) --------

    def _build_system(self, text: str) -> Dict[str, str]:
        text = text.strip()
        if not text:
            text = (
                "You are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure. "
                "Be descriptive and fair, follow SRD rules, and always narrate from the DM’s perspective. "
                "Keep narration to 2–4 sentences."
            )
        return {"role": "system", "content": text}

    def _build_developer(self, text: Optional[str], in_combat: bool, contract: Optional[Dict]) -> Optional[Dict[str, str]]:
        base = (
            "All responses must be VALID JSON per the Output Schema. "
            "Never include markdown or prose outside JSON. "
            "Use outcome checks for uncertain actions; do not invent dice results. "
            "Propose only deltas for updates; do not overwrite full state. "
        )
        if in_combat:
            base += (
                "While in_combat, describe short rounds; do not resolve entire combat in one reply. "
                "Offer clear next actions each turn."
            )
        if text:
            base = text.strip() + "\n" + base
        return {"role": "developer", "content": base}

    def _build_user(
        self,
        story_brief: str,
        character: str,
        status: str,
        recent: str,
        rules: str,
        player: str,
        output_schema: str,
    ) -> Dict[str, str]:
        sections = []

        sections.append("## Intro\nYou are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure.\n"
                        "Speak from the DM’s perspective; keep narration concise and immersive.")

        sections.append("## Game Rules\n" + rules)

        sections.append("## Story\n" + story_brief)

        sections.append("### Character\n" + character)

        sections.append("## Status\n" + status)

        if recent:
            sections.append("## Recent\n" + recent)

        sections.append("## Player\n" + player)

        sections.append("## Output Schema\n" + output_schema)

        # Join with blank lines—this becomes a single compact user content block.
        content = "\n\n".join(s for s in sections if s.strip())
        return {"role": "user", "content": content}
