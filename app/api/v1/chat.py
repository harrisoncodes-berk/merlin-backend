from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.dependencies.auth import require_user_id
from app.schemas.chat import (
    Session,
    SessionRequest,
    HistoryResponse,
    SendMessageRequest,
    Message,
)
from app.repos.chat_repo import ChatRepo
from app.adapters.db import get_db_session

chat_router = APIRouter(prefix="/chat", tags=["chat"])
repo = ChatRepo()


@chat_router.get("/sessions/{session_id}", response_model=Session)
async def session(
    session_id: str,
    user_id: str = Depends(require_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await repo.get_session(db_session, user_id, session_id)


@chat_router.post("/sessions/active", response_model=Session)
async def active_session(
    payload: SessionRequest,
    user_id: str = Depends(require_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    session = await repo.get_or_create_active_session(
        db_session, user_id, payload.characterId, payload.title, payload.settings or {}
    )
    await db_session.commit()
    return session


@chat_router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def history(
    session_id: str,
    after: Optional[int] = None,
    limit: int = 50,
    user_id: str = Depends(require_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        await repo.assert_owned_session(db_session, user_id, session_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")

    limit = max(1, min(limit, 200))
    msgs = await repo.list_messages(db_session, session_id, after=after, limit=limit)

    if after is None:
        total = await repo.count_total_messages(db_session, session_id)
        has_more = total > len(msgs)
    else:
        has_more = len(msgs) > 0

    return {
        "sessionId": session_id,
        "messages": [
            {
                "messageId": m["message_id"],
                "role": m["role"],
                "content": m["content"],
                "createdAt": m["created_at"],
            }
            for m in msgs
        ],
        "hasMore": has_more,
    }


@chat_router.post("/sessions/{session_id}/message", response_model=Message)
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    user_id: str = Depends(require_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        msg = await repo.send_message_return_assistant(
            db_session, user_id, session_id, payload.message
        )
        await db_session.commit()
        return msg
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
