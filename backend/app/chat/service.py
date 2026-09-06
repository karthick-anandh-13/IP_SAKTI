from sqlalchemy.orm import Session, joinedload

from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate


def create_session(db: Session, user_id: str, payload: ChatSessionCreate) -> ChatSession:
    session = ChatSession(
        user_id=user_id,
        title=payload.title,
        language=payload.language,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, user_id: str) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


def get_session(db: Session, session_id: str, user_id: str) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .options(joinedload(ChatSession.messages))
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def delete_session(db: Session, session_id: str, user_id: str) -> bool:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def add_message(db: Session, session: ChatSession, payload: ChatMessageCreate) -> ChatMessage:
    message = ChatMessage(
        session_id=session.id,
        sender=payload.sender,
        message=payload.message,
        source_citation=payload.source_citation,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
