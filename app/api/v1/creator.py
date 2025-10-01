from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_session
from app.dependencies.auth import require_user_id
from app.repos.creator_repo import list_backgrounds, list_classes, list_races, create_character
from app.schemas.creator import Background, Class, Race, CharacterDraft
from app.schemas.character import Character

router = APIRouter(prefix="/creator", tags=["creator"])

@router.get("/races", response_model=List[Race])
async def get_races(session: AsyncSession = Depends(get_session)):
    return await list_races(session)

@router.get("/classes", response_model=List[Class])
async def get_classes(session: AsyncSession = Depends(get_session)):
    return await list_classes(session)

@router.get("/backgrounds", response_model=List[Background])
async def get_backgrounds(session: AsyncSession = Depends(get_session)):
    return await list_backgrounds(session)


@router.post("/characters", response_model=Character)
async def create_character_endpoint(
    character_draft: CharacterDraft,
    user_id: str = Depends(require_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Create a new character from a character draft."""
    try:
        return await create_character(session, user_id, character_draft)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create character: {str(e)}")