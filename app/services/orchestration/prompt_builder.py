from typing import List

from app.domains.character import Character
from app.domains.chat import Message
from app.adapters.llm.types import PromptPayload

INTRO_PROMPT = """You are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure. Speak from the DM’s perspective and keep narration immersive but concise."""
STANDARD_RULES_PROMPT = """Rules:
1. Utilize the character's abilities and skills to resolve ability/skill checks.
2. If the character tries to use an item, check if the item is in the character's inventory. If not, respond with "You don't have that item."
3. Reference the chat history to maintain consistency in the story.
4. Be creative in adding details to the story such as descriptions of the environment, characters, and actions.
5. If the user provides a question, answer it based on the story and the character's knowledge or apply a dice roll to resolve the question.
6. If the character enters combat, create the npc for a level 1 enemy and use the chat history to determine what happens next.
7. Enfore relative realism for medieval fantasy. If the character tries to do something that is not possible, respond with "That is not possible."
8. Keep responses to within 2 to 4 sentences.
9. Provide all responses to the user in JSON format with no other text.
10. Output Schema:
{
    "message_to_user": string
}
""".strip()


class PromptBuilder:
    def build_standard_prompt(
        self,
        user_message: str,
        character: Character,
        messages: List[Message],
    ) -> PromptPayload:
        user_part_character = "## Character Sheet\n" + self._render_character(character)

        user_part_conversation = "## Conversation\n" + self._render_conversation(
            messages
        )

        user_part_user_message = "## Latest User Message to respond to\n" + user_message

        user_part_task = (
            "## Task\n"
            "Continue the story as Merlin. Follow the rules. "
            "Respond ONLY with a JSON object matching the Output Schema."
        )

        return PromptPayload(
            system_messages=[INTRO_PROMPT, STANDARD_RULES_PROMPT],
            user_messages=[
                user_part_character,
                user_part_conversation,
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
