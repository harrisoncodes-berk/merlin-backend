from typing import Optional, List
from sqlalchemy import select, insert, func, literal_column
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character_tables import characters
from app.models.chat_tables import chat_sessions, chat_messages
from app.domains.chat import Message, Session
from app.domains.adventures import AdventureStatus


class ChatRepo:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def assert_owned_session(self, user_id: str, session_id: str) -> None:
        stmt = (
            select(literal_column("1"))
            .select_from(chat_sessions)
            .where(
                chat_sessions.c.session_id == session_id,
                chat_sessions.c.user_id == user_id,
            )
        )
        row = (await self.db_session.execute(stmt)).first()
        if row is None:
            raise NoResultFound("session not found or not owned")

    async def assert_owned_character(self, user_id: str, character_id: str) -> None:
        stmt = (
            select(literal_column("1"))
            .select_from(characters)
            .where(
                characters.c.character_id == character_id,
                characters.c.user_id == user_id,
            )
        )
        row = (await self.db_session.execute(stmt)).first()
        if row is None:
            raise NoResultFound("character not found or not owned")

    async def get_session(self, user_id: str, session_id: str) -> Optional[Session]:
        stmt = select(
            chat_sessions.c.session_id,
            chat_sessions.c.character_id,
            chat_sessions.c.adventure_title,
            chat_sessions.c.story_brief,
            chat_sessions.c.status,
            chat_sessions.c.created_at,
            chat_sessions.c.updated_at,
            chat_sessions.c.archived_at,
        ).where(
            chat_sessions.c.user_id == user_id,
            chat_sessions.c.session_id == session_id,
        )
        rec = (await self.db_session.execute(stmt)).first()
        if not rec:
            raise NoResultFound("session not found")
        return _row_to_session(rec)

    async def get_session_for_character(
        self, user_id: str, character_id: str
    ) -> Optional[Session]:
        stmt = select(
            chat_sessions.c.session_id,
            chat_sessions.c.character_id,
            chat_sessions.c.adventure_title,
            chat_sessions.c.story_brief,
            chat_sessions.c.status,
        ).where(
            chat_sessions.c.user_id == user_id,
            chat_sessions.c.character_id == character_id,
        )
        rec = (await self.db_session.execute(stmt)).first()
        if not rec:
            return None
        return _row_to_session(rec)

    async def create_session(
        self,
        user_id: str,
        character_id: str,
        adventure_title: str,
        story_brief: str,
        status: AdventureStatus,
    ) -> Session:
        stmt = (
            insert(chat_sessions)
            .values(
                user_id=user_id,
                character_id=character_id,
                adventure_title=adventure_title,
                story_brief=story_brief,
                status=status,
            )
            .returning(
                chat_sessions.c.session_id,
                chat_sessions.c.character_id,
                chat_sessions.c.adventure_title,
                chat_sessions.c.story_brief,
                chat_sessions.c.status,
                chat_sessions.c.created_at,
                chat_sessions.c.updated_at,
                chat_sessions.c.archived_at,
            )
        )
        rec = (await self.db_session.execute(stmt)).first()
        return _row_to_session(rec)

    async def list_messages(
        self,
        session_id: str,
        after: Optional[int],
        limit: int,
    ) -> List[Message]:
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
            rows = (await self.db_session.execute(stmt)).all()
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
            rows = (await self.db_session.execute(stmt)).all()

        return [_row_to_message(r) for r in rows]

    async def count_total_messages(self, session_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(chat_messages)
            .where(chat_messages.c.session_id == session_id)
        )
        return int((await self.db_session.execute(stmt)).scalar_one())

    async def insert_user_message_row(self, session_id: str, content: str) -> Message:
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
        r = (await self.db_session.execute(stmt)).first()
        return _row_to_message(r)

    async def insert_assistant_message_row(
        self, session_id: str, content: str
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
        r = (await self.db_session.execute(stmt)).first()
        return _row_to_message(r)


def _row_to_session(r) -> Session:
    print(r)
    return Session(
        session_id=str(r.session_id),
        character_id=str(r.character_id),
        adventure_title=r.adventure_title,
        story_brief=r.story_brief,
        status=AdventureStatus(**r.status),
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat(),
        archived_at=r.archived_at.isoformat() if r.archived_at else None,
    )


def _row_to_message(r) -> Message:
    return Message(
        message_id=int(r.message_id),
        role=r.role,
        content=r.content,
        created_at=r.created_at.isoformat(),
    )
