from typing import List

from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.chat import Message
from app.adapters.llm.types import PromptPayload

STANDARD_RULES_PROMPT = """
You are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure. Speak from the DM’s perspective and keep narration immersive but concise.
# Rules:
## General
* Be creative in adding details to the story such as descriptions of the environment, characters, and actions
* If the user provides a question, answer it based on the story and the character's knowledge
* Enfore relative realism for medieval fantasy
* If the character tries to do something that is not possible, respond with "That is not possible."
* Keep messages to user within 2 to 4 sentences
* Keep the story moving
* Reference the chat history to maintain consistency in the story
## Ability Checks
* Utilize the ability_check tool to check if the character succeeds at an action.
* Decide what happens next in the story based on the result of the ability check.
## Adventure Status
* The summary field should be an ongoing summary of what the character has done and what has happened in the story so far
* Keep the summary under 10 sentences and only include key information
* Location should be a short description of the current location
* Combat state should be true if the character is in combat, false otherwise
""".strip()


class PromptBuilder:
    def build_standard_prompt(
        self,
        story_brief: str,
        adventure_status: AdventureStatus,
        chat_history: List[Message],
        user_message: str,
        character: Character,
    ) -> PromptPayload:
        user_part_story_brief = "## Story Brief\n" + story_brief

        user_part_adventure_status = (
            "## Adventure Status\n" + self._render_adventure_status(adventure_status)
        )

        user_part_chat_history = "## Chat History\n" + self._render_conversation(chat_history)

        user_part_character = "## Character Sheet\n" + self._render_character(character)

        user_part_user_message = "## Latest User Message to respond to\n" + user_message

        user_part_task = (
            "## Task\n"
            "Continue the story as Merlin. Follow the rules. "
            "Respond ONLY with a JSON object matching the Output Schema."
        )

        return PromptPayload(
            system_messages=[STANDARD_RULES_PROMPT],
            user_messages=[
                user_part_story_brief,
                user_part_adventure_status,
                user_part_chat_history,
                user_part_character,
                user_part_user_message,
                user_part_task,
            ],
        )

    def build_followup_prompt(self) -> str:
        return "Continue the scene. Respond ONLY with the JSON schema defined earlier."

    def build_combat_prompt(self) -> str:
        return (
            "Enter combat mode. Create a level 1 enemy and resolve actions per rules."
        )

    def _render_adventure_status(self, adventure_status: AdventureStatus) -> str:
        return (
            f"Summary: {adventure_status.summary}\n"
            f"Location: {adventure_status.location}\n"
            f"Combat State: {adventure_status.combat_state}"
        )

    def _render_character(self, c: Character) -> str:
        abilities = c.abilities
        abl = (
            f"STRENGTH {abilities.str}  DEXTERITY {abilities.dex}  CONSTITUTION {abilities.con}  "
            f"INTELLIGENCE {abilities.int}  WISDOM {abilities.wis}  CHARISMA {abilities.cha}"
        )

        skills = (
            ", ".join(
                getattr(s, "key", getattr(s, "name", str(s))) for s in (c.skills or [])
            )
            or "None"
        )

        features = (
            "; ".join(
                f"{getattr(f, 'name', 'Feature')}: {getattr(f, 'description', '')}".strip(
                    ": "
                )
                for f in (c.features or [])
            )
            or "None"
        )

        items = (
            "; ".join(
                f"{getattr(i, 'name', 'Item')}"
                + (
                    f" x{getattr(i, 'quantity', 1)}"
                    if getattr(i, "quantity", 1) != 1
                    else ""
                )
                for i in (c.inventory or [])
            )
            or "Empty"
        )

        if c.spellcasting:
            sc = c.spellcasting
            spells_list = (
                ", ".join(getattr(s, "name", str(s)) for s in (sc.spells or []))
                or "None"
            )
            ability = getattr(sc, "ability", "N/A")
            spellcasting = f"Ability: {ability} | Spells: {spells_list}"
        else:
            spellcasting = "None"

        return (
            f"Name: {c.name}\n"
            f"Race: {c.race} | Class: {c.class_name} | Background: {c.background} | Level: {c.level}\n"
            f"HP: {c.hp_current}/{c.hp_max} | AC: {c.ac} | Speed: {c.speed}\n"
            f"Abilities: {abl}\n"
            f"Skills: {skills}\n"
            f"Features: {features}\n"
            f"Inventory: {items}\n"
            f"Spellcasting: {spellcasting}"
        )

    def _render_conversation(self, msgs: List[Message]) -> str:
        if not msgs:
            return "No prior messages."
        lines = []
        for m in msgs:
            role = m.role.upper()
            content = (m.content or "").strip()
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
