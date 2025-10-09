from typing import List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_db_session
from app.dependencies.auth import require_user_id
from app.mappers.creator_mappers import create_character_in_to_command
from app.repos.creator_repo import CreatorRepo
from app.schemas.creator import BackgroundOut, ClassOut, CreateCharacterIn, RaceOut
from app.schemas.character import CharacterOut
from app.services.character.create_character_service import CreateCharacterService

router = APIRouter(prefix="/creator", tags=["creator"])


def get_creator_repo(
    db_session: AsyncSession = Depends(get_db_session),
) -> CreatorRepo:
    return CreatorRepo(db_session)


def get_create_character_service(
    creator_repo: CreatorRepo = Depends(get_creator_repo),
) -> CreateCharacterService:
    return CreateCharacterService(creator_repo)


@router.get("/races", response_model=List[RaceOut])
async def get_races(creator_repo: CreatorRepo = Depends(get_creator_repo)):
    races = await creator_repo.list_races()
    return [RaceOut.model_validate(r) for r in races]


@router.get("/classes", response_model=List[ClassOut])
async def get_classes(creator_repo: CreatorRepo = Depends(get_creator_repo)):
    classes = await creator_repo.list_classes()
    return [ClassOut.model_validate(c) for c in classes]


@router.get("/backgrounds", response_model=List[BackgroundOut])
async def get_backgrounds(creator_repo: CreatorRepo = Depends(get_creator_repo)):
    backgrounds = await creator_repo.list_backgrounds()
    return [BackgroundOut.model_validate(b) for b in backgrounds]


@router.post("/characters", response_model=CharacterOut)
async def create_character_endpoint(
    create_character_in: CreateCharacterIn,
    create_character_service: CreateCharacterService = Depends(
        get_create_character_service
    ),
    user_id: str = Depends(require_user_id),
):
    """Create a new character from a character draft."""
    create_character_command = create_character_in_to_command(create_character_in)
    try:
        return await create_character_service.create_character(
            user_id, create_character_command
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create character: {str(e)}"
        )
