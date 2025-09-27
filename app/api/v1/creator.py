from typing import List
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db import get_session
from app.repos.creator_repo import list_backgrounds, list_classes, list_races
from app.schemas.creator import Background, Class, Race

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