from typing import List
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_session
from app.repos.creator_repo import list_races, list_classes
from app.schemas.creator import Race, Class

router = APIRouter(prefix="/creator", tags=["creator"])

@router.get("/races", response_model=List[Race])
async def get_races(session: AsyncSession = Depends(get_session)):
    return await list_races(session)

@router.get("/classes", response_model=List[Class])
async def get_classes(session: AsyncSession = Depends(get_session)):
    return await list_classes(session)

