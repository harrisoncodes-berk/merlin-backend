from typing import List
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_session
from app.repos.creator_repo import list_races
from app.schemas.creator import Race

router = APIRouter(prefix="/creator", tags=["creator"])

@router.get("/races", response_model=List[Race])
async def get_races(session: AsyncSession = Depends(get_session)):
    return await list_races(session)
