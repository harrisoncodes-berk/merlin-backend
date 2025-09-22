from fastapi import APIRouter, Depends
from app.schemas.auth import CurrentUser
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["auth"])


@router.get("/me", response_model=CurrentUser)
async def me(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
