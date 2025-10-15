from uuid import uuid4

from app.domains.character import Character, Spellcasting, SpellSlots
from app.domains.creator import CreateCharacterCommand, CreatorRepoProtocol


class CreateCharacterService:
    def __init__(self, creator_repo: CreatorRepoProtocol):
        self.creator_repo = creator_repo

    async def create_character(
        self, user_id: str, create_character_command: CreateCharacterCommand
    ) -> Character:
        character_race = await self.creator_repo.get_race(
            create_character_command.race_id
        )
        character_class = await self.creator_repo.get_class(
            create_character_command.class_id
        )
        character_background = await self.creator_repo.get_background(
            create_character_command.background_id
        )
    
        con_modifier = (create_character_command.abilities.con - 10) // 2
        dex_modifier = (create_character_command.abilities.dex - 10) // 2

        hit_dice = character_class.hit_dice
        hp_max = hit_dice.sides + con_modifier
        ac = character_class.ac + dex_modifier
        speed = character_race.speed


        spellcasting_data = None
        if create_character_command.spells:
            spellcasting_data = Spellcasting(
                ability="int",  # Default to intelligence for now
                slots={
                    "1": SpellSlots(
                        max=2,
                        used=0,
                    ),
                },
                spells=create_character_command.spells,
            )

        inventory = []
        for weapon in create_character_command.weapons:
            inventory.append(
                {
                    "id": weapon.id,
                    "name": weapon.name,
                    "weight": weapon.weight,
                    "quantity": weapon.quantity,
                    "description": weapon.description,
                }
            )
        for background_item in character_background.inventory:
            inventory.append(
                {
                    "id": background_item.id,
                    "name": background_item.name,
                    "weight": background_item.weight,
                    "quantity": background_item.quantity,
                    "description": background_item.description,
                }
            )

        character = Character(
            id=str(uuid4()),
            name=create_character_command.name,
            race=character_race.name,
            class_name=character_class.name,
            background=character_background.name,
            level=1,
            hp_current=hp_max,
            hp_max=hp_max,
            ac=ac,
            speed=speed,
            abilities=create_character_command.abilities,
            skills=create_character_command.skills,
            features=(character_race.features or [])
            + (character_class.features or [])
            + (character_background.features or []),
            inventory=inventory,
        )
        if spellcasting_data is not None:
            character.spellcasting = spellcasting_data

        created_character = await self.creator_repo.create_character(user_id, character)

        await self.creator_repo.db_session.commit()

        return created_character
