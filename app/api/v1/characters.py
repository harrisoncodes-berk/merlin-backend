from typing import List
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_db_session
from app.dependencies.auth import require_user_id
from app.schemas.character import CharacterOut
from app.repos.character_repo import CharacterRepo

router = APIRouter(prefix="/characters", tags=["characters"])


def get_character_repo(
    db_session: AsyncSession = Depends(get_db_session),
) -> CharacterRepo:
    return CharacterRepo(db_session)


@router.get("", response_model=List[CharacterOut])
async def list_my_characters(
    user_id: str = Depends(require_user_id),
    character_repo: CharacterRepo = Depends(get_character_repo),
):
    characters = await character_repo.list_characters_for_user(user_id)
    return [CharacterOut.model_validate(c) for c in characters]


@router.get("/{id}", response_model=CharacterOut)
async def get_my_character(
    id: str,
    user_id: str = Depends(require_user_id),
    character_repo: CharacterRepo = Depends(get_character_repo),
):
    c = await character_repo.get_character_by_character_id(user_id, id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterOut.model_validate(c)
