# tests/test_prompt_builder.py
import re
import pytest

from app.services.orchestration.prompt_builder import (
    PromptBuilder,
    PromptInput,
    Status,
    RecentTurn,
)

"""
To run the test:
PYTHONPYCACHEPREFIX="$PWD/.pycache" pytest -q tests/unit/services/orchestration/test_prompt_builder.py
"""

@pytest.fixture
def builder() -> PromptBuilder:
    return PromptBuilder()

@pytest.fixture
def base_prompt_input() -> PromptInput:
    return PromptInput(
        system_text=(
            "You are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure. "
            "Be descriptive and fair, follow SRD rules, and narrate from the DM’s perspective."
        ),
        developer_text=(
            "Output must be strict JSON. Ask for outcome checks when results are uncertain. "
            "Include updates only when something changes."
        ),
        story_brief="Infiltrate Stormspire Keep to rescue Princess Seraphine.",
        character_block=(
            "Name: Tbitty Shortfellow\n"
            "Race: Halfling\nClass: Rogue\nBackground: Criminal\n"
            "HP: 20\nAC: 14\nInventory: Crowbar, Lockpicks, Dagger\n"
        ),
        status=Status(
            summary="Hiding in the forest outside the keep, scouting patrol routes.",
            location="Forest outside the castle walls",
            in_combat=False,
        ),
        recent_turns=[
            RecentTurn(user="I creep toward the outer wall.", dm="You spot a loose stone near a drain.")
        ],
        player_text="I examine the drain for a way in.",
        flags={"in_combat": False},
    )

# -------------------------
# Tests
# -------------------------

def test_message_roles_and_order(builder: PromptBuilder, base_prompt_input: PromptInput):
    msgs = builder.build(base_prompt_input)
    assert len(msgs) == 3
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "developer"
    assert msgs[2]["role"] == "user"

def test_sections_present_in_user_block(builder: PromptBuilder, base_prompt_input: PromptInput):
    msgs = builder.build(base_prompt_input)
    user = msgs[2]["content"]

    # Headings we expect the builder to include
    for heading in ["## Intro", "## Game Rules", "## Story", "### Character", "## Status", "## Player", "## Output Schema"]:
        assert heading in user

    # Bits of our provided content should show up
    assert "Infiltrate Stormspire Keep" in user
    assert "Tbitty Shortfellow" in user
    assert "Forest outside the castle walls" in user
    assert "I examine the drain for a way in." in user

def test_default_output_schema_text_present_when_no_contract(builder: PromptBuilder, base_prompt_input: PromptInput):
    msgs = builder.build(base_prompt_input)
    user = msgs[2]["content"]
    assert "OUTPUT SCHEMA (JSON):" in user
    # A few schema hints we rely on:
    assert '"message_to_user":' in user
    assert '"updates":' in user
    assert '"outcome_check":' in user

def test_in_combat_rules_injected_when_flag_true(builder: PromptBuilder, base_prompt_input: PromptInput):
    # Flip combat on
    pi = base_prompt_input
    pi.flags = {"in_combat": True}
    pi = PromptInput(**{**pi.__dict__})  # create a new frozen-equivalent copy

    msgs = builder.build(pi)
    dev = msgs[1]["content"]
    user = msgs[2]["content"]

    # Developer content should mention combat pacing
    assert "While in_combat" in dev

    # Rules section in user block should include combat line
    assert re.search(r"While in_combat:.*attack = d20 \+ bonus vs AC", user)

def test_character_block_takes_precedence_over_brief(builder: PromptBuilder, base_prompt_input: PromptInput):
    # Provide both block and brief; block should win
    pi = base_prompt_input
    pi = PromptInput(
        **{
            **pi.__dict__,
            "character_brief": "Tbitty — L2 Halfling Rogue (HP 20/20, AC 14)",
        }
    )
    msgs = builder.build(pi)
    user = msgs[2]["content"]

    # Expect the block's multiline details, not just the brief line
    assert "Name: Tbitty Shortfellow" in user
    assert "Tbitty — L2 Halfling Rogue" not in user  # the brief should be ignored

def test_clipping_applies_ellipsis(builder: PromptBuilder, base_prompt_input: PromptInput):
    # Constrain max chars to force clipping with an ellipsis
    tiny_limits = {
        "story_brief": 20,
        "character_block": 30,
        "character_brief": 30,
        "status": 25,
        "recent_turn_line": 25,
        "player_text": 25,
    }
    pi = PromptInput(
        **{
            **base_prompt_input.__dict__,
            "max_chars": tiny_limits,
        }
    )

    msgs = builder.build(pi)
    user = msgs[2]["content"]

    # We should see ellipses in multiple places
    assert "Infiltrate Stormspi…" in user or "Infiltrate Stormspire…" in user
    # Either the character block or status should be clipped
    assert "…" in user

def test_recent_turns_rendered(builder: PromptBuilder, base_prompt_input: PromptInput):
    msgs = builder.build(base_prompt_input)
    user = msgs[2]["content"]

    assert "## Recent" in user
    assert "- You: I creep toward the outer wall." in user
    assert "- DM: You spot a loose stone near a drain." in user

def test_developer_defaults_present_even_when_none(builder: PromptBuilder, base_prompt_input: PromptInput):
    # Remove developer_text; builder should still provide its base developer guidance
    pi = PromptInput(
        **{
            **base_prompt_input.__dict__,
            "developer_text": None,
        }
    )
    msgs = builder.build(pi)
    dev = msgs[1]["content"]
    assert "VALID JSON" in dev.upper()  # base guidance about valid JSON
    assert "outcome checks" in dev.lower()

def test_no_status_provided_is_handled_gracefully(builder: PromptBuilder, base_prompt_input: PromptInput):
    pi = PromptInput(
        **{
            **base_prompt_input.__dict__,
            "status": None,
        }
    )
    msgs = builder.build(pi)
    user = msgs[2]["content"]
    assert "## Status" in user
    assert "(No status provided)" in user
