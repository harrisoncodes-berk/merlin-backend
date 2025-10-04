from typing import Optional, List, Dict, Any
from sqlalchemy import select, insert, func, literal_column
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_tables import chat_sessions, chat_messages


class ChatRepo:
    async def ensure_session(
        self,
        db_session: AsyncSession,
        user_id: str,
        title: Optional[str],
        settings: Dict[str, Any],
    ):
        t = (title or "New Adventure").strip() or "New Adventure"
        stmt = (
            insert(chat_sessions)
            .values(user_id=user_id, title=t, settings=settings)
            .returning(
                chat_sessions.c.session_id,
                chat_sessions.c.title,
                chat_sessions.c.settings,
                chat_sessions.c.created_at,
            )
        )
        rec = (await db_session.execute(stmt)).first()
        return {
            "session_id": str(rec.session_id),
            "title": rec.title,
            "settings": rec.settings or {},
            "created_at": rec.created_at.isoformat(),
        }

    async def assert_owned_session(
        self, db_session: AsyncSession, user_id: str, session_id: str
    ) -> None:
        stmt = (
            select(literal_column("1"))
            .select_from(chat_sessions)
            .where(
                chat_sessions.c.session_id == session_id,
                chat_sessions.c.user_id == user_id,
            )
        )
        row = (await db_session.execute(stmt)).first()
        if row is None:
            raise NoResultFound("session not found or not owned")

    async def list_messages(
        self,
        db_session: AsyncSession,
        session_id: str,
        after: Optional[int],
        limit: int,
    ) -> List[dict]:
        if after is not None:
            stmt = (
                select(
                    chat_messages.c.message_id,
                    chat_messages.c.role,
                    chat_messages.c.content,
                    chat_messages.c.created_at,
                )
                .where(
                    chat_messages.c.session_id == session_id,
                    chat_messages.c.message_id > after,
                )
                .order_by(chat_messages.c.message_id.asc())
                .limit(limit)
            )
            rows = (await db_session.execute(stmt)).all()
        else:
            inner = (
                select(
                    chat_messages.c.message_id,
                    chat_messages.c.role,
                    chat_messages.c.content,
                    chat_messages.c.created_at,
                )
                .where(chat_messages.c.session_id == session_id)
                .order_by(chat_messages.c.message_id.desc())
                .limit(limit)
                .subquery()
            )
            stmt = select(
                inner.c.message_id,
                inner.c.role,
                inner.c.content,
                inner.c.created_at,
            ).order_by(inner.c.message_id.asc())
            rows = (await db_session.execute(stmt)).all()

        return [
            {
                "message_id": r.message_id,
                "role": r.role,
                "content": r.content,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]

    async def count_total_messages(
        self, db_session: AsyncSession, session_id: str
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(chat_messages)
            .where(chat_messages.c.session_id == session_id)
        )
        return int((await db_session.execute(stmt)).scalar_one())

    async def insert_user_message(
        self, db_session: AsyncSession, session_id: str, content: str
    ) -> int:
        stmt = (
            insert(chat_messages)
            .values(session_id=session_id, role="user", content=content)
            .returning(chat_messages.c.message_id)
        )
        mid = int((await db_session.execute(stmt)).scalar_one())
        return mid

    async def insert_assistant_message(
        self, db_session: AsyncSession, session_id: str, content: str
    ) -> int:
        stmt = (
            insert(chat_messages)
            .values(session_id=session_id, role="assistant", content=content)
            .returning(chat_messages.c.message_id)
        )
        mid = int((await db_session.execute(stmt)).scalar_one())
        return mid
