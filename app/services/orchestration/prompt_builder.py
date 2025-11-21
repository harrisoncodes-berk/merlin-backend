import json
from typing import List

from app.domains.adventures import AdventureStatus
from app.domains.character import Character
from app.domains.chat import Message
from app.adapters.llm.types import (
    FunctionCall,
    FunctionCallOutput,
    InputMessage,
    PromptPayload,
)

STANDARD_RULES_PROMPT = """
You are Merlin, a Dungeon Master guiding a Dungeons & Dragons adventure. Speak from the DM’s perspective and keep narration immersive but concise.
## Rules:
* Be creative in adding details to the story such as descriptions of the environment, characters, and actions
* If the user provides a question, answer it based on the story and the character's knowledge
* Enfore relative realism for medieval fantasy
* If the character tries to do something that is not possible, respond with "That is not possible."
* Keep messages to user within 2 to 4 sentences
* Keep the story moving
* Reference the chat history to maintain consistency in the story
* Call any tools that are relevant to the user's message.
* If no tools are necessary, respond with a message to the user.
""".strip()


class PromptBuilder:
    def __init__(
        self,
        story_brief: str,
        character: Character,
        adventure_status: AdventureStatus,
        chat_history: List[Message],
    ):
        self.story_brief = story_brief
        self.character = character
        self.adventure_status = adventure_status
        self.chat_history = chat_history
        self.prompt_payload = self.build_standard_prompt()

    def build_standard_prompt(self) -> PromptPayload:
        story_brief = "## Story Brief\n" + self.story_brief

        character = "## Character Details\n" + self._render_character()

        adventure_status = "## Adventure Status\n" + self._render_adventure_status()

        chat_history = self._render_chat_history()

        return PromptPayload(
            messages=[
                InputMessage(role="system", content=STANDARD_RULES_PROMPT),
                InputMessage(role="system", content=story_brief),
                InputMessage(role="system", content=character),
                InputMessage(role="system", content=adventure_status),
            ]
            + chat_history,
        )

    def add_function_call_messages(
        self, call_id: str, name: str, arguments: dict, output: bool
    ):
        function_call = FunctionCall(
            call_id=call_id, name=name, arguments=json.dumps(arguments)
        )
        function_call_output = FunctionCallOutput(call_id=call_id, output=output)
        self.prompt_payload.messages.append(function_call)
        self.prompt_payload.messages.append(function_call_output)

    def _render_adventure_status(self) -> str:
        return (
            f"Summary: {self.adventure_status.summary}\n"
            f"Location: {self.adventure_status.location}\n"
            f"Combat State: {self.adventure_status.combat_state}"
        )

    def _render_character(self) -> str:
        return (
            f"Name: {self.character.name}\n"
            f"Race: {self.character.race} | Class: {self.character.class_name} | Background: {self.character.background}\n"
        )

    def _render_chat_history(self) -> list[InputMessage]:
        return [InputMessage(role=m.role, content=m.content) for m in self.chat_history]
