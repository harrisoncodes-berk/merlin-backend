from typing import List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_session
from app.dependencies.auth import require_user_id
from app.repos.character_repo import list_characters_for_user, get_character_for_user
from app.schemas.character import CharacterOut

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=List[CharacterOut])
async def list_my_characters(
    user_id: str = Depends(require_user_id),
    session: AsyncSession = Depends(get_session),
):
    return await list_characters_for_user(session, user_id)


@router.get("/{id}", response_model=CharacterOut)
async def get_my_character(
    id: str,
    user_id: str = Depends(require_user_id),
    session: AsyncSession = Depends(get_session),
):
    ch = await get_character_for_user(session, user_id, id)
    if not ch:
        raise HTTPException(status_code=404, detail="Character not found")
    return ch
