from typing import Optional, List, Dict, Any
from sqlalchemy import select, insert, func, literal_column
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character_tables import characters
from app.models.chat_tables import chat_sessions, chat_messages
from app.schemas.chat import Message, Session


class ChatRepo:
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

    async def assert_owned_character(
        self, db_session: AsyncSession, user_id: str, character_id: str
    ) -> None:
        stmt = (
            select(literal_column("1"))
            .select_from(characters)
            .where(
                characters.c.character_id == character_id,
                characters.c.user_id == user_id,
            )
        )
        row = (await db_session.execute(stmt)).first()
        if row is None:
            raise NoResultFound("character not found or not owned")

    async def get_session(
        self, db_session: AsyncSession, user_id: str, session_id: str
    ) -> Session:
        stmt = select(
            chat_sessions.c.session_id,
            chat_sessions.c.character_id,
            chat_sessions.c.title,
            chat_sessions.c.settings,
            chat_sessions.c.created_at,
            chat_sessions.c.updated_at,
            chat_sessions.c.archived_at,
        ).where(
            chat_sessions.c.user_id == user_id,
            chat_sessions.c.session_id == session_id,
        )
        rec = (await db_session.execute(stmt)).first()
        if not rec:
            raise NoResultFound("session not found")
        return _session_row_to_out(rec)

    async def create_session(
        self,
        db_session: AsyncSession,
        user_id: str,
        character_id: str,
        title: Optional[str],
        settings: Dict[str, Any],
    ) -> Session:
        t = (title or "New Adventure").strip() or "New Adventure"
        stmt = (
            insert(chat_sessions)
            .values(
                user_id=user_id, character_id=character_id, title=t, settings=settings
            )
            .returning(
                chat_sessions.c.session_id,
                chat_sessions.c.character_id,
                chat_sessions.c.title,
                chat_sessions.c.settings,
                chat_sessions.c.created_at,
                chat_sessions.c.updated_at,
                chat_sessions.c.archived_at,
            )
        )
        rec = (await db_session.execute(stmt)).first()
        return _session_row_to_out(rec)

    async def get_or_create_active_session(
        self,
        db_session: AsyncSession,
        user_id: str,
        character_id: str,
        title: Optional[str],
        settings: Dict[str, Any],
    ) -> Session:
        stmt = (
            select(
                chat_sessions.c.session_id,
                chat_sessions.c.character_id,
                chat_sessions.c.title,
                chat_sessions.c.settings,
                chat_sessions.c.created_at,
                chat_sessions.c.updated_at,
                chat_sessions.c.archived_at,
            )
            .where(
                chat_sessions.c.user_id == user_id,
                chat_sessions.c.character_id == character_id,
                chat_sessions.c.archived_at.is_(None),
            )
            .order_by(chat_sessions.c.created_at.desc())
            .limit(1)
        )
        rec = (await db_session.execute(stmt)).first()
        if rec:
            return _session_row_to_out(rec)

        try:
            return await self.create_session(
                db_session, user_id, character_id, title, settings
            )
        except IntegrityError:
            rec = (await db_session.execute(stmt)).first()
            if rec:
                return _session_row_to_out(rec)
            raise

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

        return [_message_row_to_out(r) for r in rows]

    async def count_total_messages(
        self, db_session: AsyncSession, session_id: str
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(chat_messages)
            .where(chat_messages.c.session_id == session_id)
        )
        return int((await db_session.execute(stmt)).scalar_one())

    async def insert_user_message_row(
        self, db_session: AsyncSession, session_id: str, content: str
    ) -> Message:
        stmt = (
            insert(chat_messages)
            .values(session_id=session_id, role="user", content=content)
            .returning(
                chat_messages.c.message_id,
                chat_messages.c.role,
                chat_messages.c.content,
                chat_messages.c.created_at,
            )
        )
        r = (await db_session.execute(stmt)).first()
        return _message_row_to_out(r)

    async def insert_assistant_message_row(
        self, db_session: AsyncSession, session_id: str, content: str
    ) -> Message:
        stmt = (
            insert(chat_messages)
            .values(session_id=session_id, role="assistant", content=content)
            .returning(
                chat_messages.c.message_id,
                chat_messages.c.role,
                chat_messages.c.content,
                chat_messages.c.created_at,
            )
        )
        r = (await db_session.execute(stmt)).first()
        return _message_row_to_out(r)

    async def send_message_return_assistant(
        self, db_session: AsyncSession, user_id: str, session_id: str, user_text: str
    ) -> dict:
        await self.assert_owned_session(db_session, user_id, session_id)

        await self.insert_user_message(db_session, session_id, user_text)

        # TODO: replace with real model inference/generation
        assistant_text = (
            "The corridor smells of damp stone and old secrets. Footsteps echo ahead."
        )

        assistant_mid = await self.insert_assistant_message(
            db_session, session_id, assistant_text
        )

        stmt = (
            select(
                chat_messages.c.message_id,
                chat_messages.c.role,
                chat_messages.c.content,
                chat_messages.c.created_at,
            )
            .where(
                chat_messages.c.session_id == session_id,
                chat_messages.c.message_id == assistant_mid,
            )
            .limit(1)
        )
        rec = (await db_session.execute(stmt)).first()
        return _message_row_to_out(rec)


def _session_row_to_out(r) -> Session:
    return Session(
        sessionId=str(r.session_id),
        characterId=str(r.character_id),
        title=r.title,
        settings=r.settings or {},
        createdAt=r.created_at.isoformat(),
        updatedAt=r.updated_at.isoformat(),
        archivedAt=r.archived_at.isoformat() if r.archived_at else None,
    )


def _message_row_to_out(r) -> Message:
    return Message(
        messageId=int(r.message_id),
        role=r.role,
        content=r.content,
        createdAt=r.created_at.isoformat(),
    )
