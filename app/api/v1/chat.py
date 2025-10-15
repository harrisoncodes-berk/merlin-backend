from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.adapters.llm.base import LLMClient
from app.adapters.db import get_db_session
from app.dependencies.auth import require_user_id
from app.schemas.chat import (
    MessageHistoryOut,
    MessageOut,
    SendMessageIn,
    SessionOut,
    SessionIn,
)
from app.repos.chat_repo import ChatRepo
from app.services.chat.turn_service import TurnService

chat_router = APIRouter(prefix="/chat", tags=["chat"])


def get_llm(request: Request) -> LLMClient:
    return request.app.state.llm


def get_chat_repo(
    db_session: AsyncSession = Depends(get_db_session),
) -> ChatRepo:
    return ChatRepo(db_session)


def get_turn_service(
    llm: LLMClient = Depends(get_llm), chat_repo: ChatRepo = Depends(get_chat_repo)
) -> TurnService:
    return TurnService(llm=llm, repo=chat_repo)


@chat_router.get("/sessions/{session_id}", response_model=SessionOut)
async def session(
    session_id: str,
    user_id: str = Depends(require_user_id),
    chat_repo: ChatRepo = Depends(get_chat_repo),
):
    s = await chat_repo.get_session(user_id, session_id)
    return SessionOut.model_validate(s)


@chat_router.post("/sessions/active", response_model=SessionOut)
async def active_session(
    payload: SessionIn,
    user_id: str = Depends(require_user_id),
    chat_repo: ChatRepo = Depends(get_chat_repo),
):
    s = await chat_repo.get_or_create_active_session(
        user_id, payload.character_id, payload.title, payload.settings or {}
    )
    await chat_repo.db_session.commit()
    return SessionOut.model_validate(s)


# TODO: Move logic to service
@chat_router.get("/sessions/{session_id}/history", response_model=MessageHistoryOut)
async def history(
    session_id: str,
    after: Optional[int] = None,
    limit: int = 50,
    user_id: str = Depends(require_user_id),
    chat_repo: ChatRepo = Depends(get_chat_repo),
):
    try:
        await chat_repo.assert_owned_session(user_id, session_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")

    limit = max(1, min(limit, 200))
    msgs = await chat_repo.list_messages(session_id, after=after, limit=limit)

    if after is None:
        total = await chat_repo.count_total_messages(session_id)
        has_more = total > len(msgs)
    else:
        has_more = len(msgs) > 0

    return MessageHistoryOut.model_validate(
        {
            "session_id": session_id,
            "messages": [MessageOut.model_validate(m) for m in msgs],
            "has_more": has_more,
        }
    )


@chat_router.post("/sessions/{session_id}/message", response_model=MessageOut)
async def send_message(
    request: Request,
    session_id: str,
    payload: SendMessageIn,
    user_id: str = Depends(require_user_id),
    chat_repo: ChatRepo = Depends(get_chat_repo),
    turn_service: TurnService = Depends(get_turn_service),
):
    try:
        await chat_repo.assert_owned_session(user_id, session_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        msg = await turn_service.handle_turn(
            user_id=user_id,
            session_id=session_id,
            user_text=payload.message,
            trace_id=getattr(request.state, "trace_id", None),
        )
        print('msg', msg)
        return MessageOut.model_validate(msg)
    except Exception as e:
        print('exception', e)
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {type(e).__name__}: {e}")
