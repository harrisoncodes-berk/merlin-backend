import dataclasses

@dataclasses.dataclass()
class UserInput:
    story_brief: str # fetch from adventures
    character_block: str # fetch from characters
    status: str # fetch from sessions

@dataclasses.dataclass()
class PromptInput:
    system_message: str # constant - intro
    developer_message: str # constant - rules
    user_message: str # dynamic - user input