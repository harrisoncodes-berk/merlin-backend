from app.domains.chat import Message, Session
from app.schemas.chat import MessageResponse, SessionResponse


def message_to_response(message: Message) -> MessageResponse:
    return MessageResponse(
        messageId=message.message_id,
        role=message.role,
        content=message.content,
        createdAt=message.created_at,
    )

def session_to_response(session: Session) -> SessionResponse:
    return SessionResponse(
        sessionId=session.session_id,
        characterId=session.character_id,
        title=session.title,
        settings=session.settings,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
        archivedAt=session.archived_at,
    )