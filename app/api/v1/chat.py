import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.dependencies.auth import require_user_id
from app.schemas.chat import (
    Session,
    SessionRequest,
    HistoryResponse,
    StreamRequest,
)
from app.repos.chat_repo import ChatRepo
from app.services.sse import sse_event
from app.services.job_registry import job_registry
from app.adapters.db import get_db_session, get_db_session_cm

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


@chat_router.post("/sessions/{session_id}/stream")
async def stream(
    session_id: str,
    req: StreamRequest,
    user_id: str = Depends(require_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        await repo.assert_owned_session(db_session, user_id, session_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Session not found")

    key = (user_id, session_id)
    if await job_registry.has(key):

        async def conflict_gen():
            yield sse_event(
                "error",
                {
                    "code": "TURN_CONFLICT",
                    "message": "Another turn is already running.",
                },
            )

        return StreamingResponse(conflict_gen(), media_type="text/event-stream")

    async def event_gen():
        current_task = asyncio.current_task()
        ok = await job_registry.try_register(key, current_task, req.clientMessageId)
        if not ok:
            yield sse_event(
                "error",
                {
                    "code": "TURN_CONFLICT",
                    "message": "Another turn is already running.",
                },
            )
            return

        try:
            async with get_db_session_cm() as db_session:
                async with db_session.begin():
                    await repo.insert_user_message(db_session, session_id, req.message)

            yield sse_event("token", {"text": "The corridor smells of damp stone"})
            await asyncio.sleep(0.6)
            yield sse_event("token", {"text": " and old secrets."})
            await asyncio.sleep(0.6)
            yield sse_event("token", {"text": " Footsteps echo ahead."})

            assistant_text = "The corridor smells of damp stone and old secrets. Footsteps echo ahead."
            async with get_db_session_cm() as db_session:
                async with db_session.begin():
                    await repo.insert_assistant_message(
                        db_session, session_id, assistant_text
                    )

            yield sse_event(
                "done",
                {"usage": {"promptTokens": 0, "completionTokens": 0, "cost": 0.0}},
            )

        except asyncio.CancelledError:
            try:
                yield sse_event(
                    "error", {"code": "CANCELLED", "message": "Turn cancelled."}
                )
            except Exception:
                pass
            raise
        except Exception as e:
            try:
                yield sse_event("error", {"code": "INTERNAL", "message": str(e)})
            finally:
                return
        finally:
            await job_registry.finish(key)

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@chat_router.delete(
    "/sessions/{session_id}/jobs/current", status_code=status.HTTP_204_NO_CONTENT
)
async def cancel(session_id: str, user_id: str = Depends(require_user_id)):
    try:
        await job_registry.cancel((user_id, session_id))
    finally:
        return
