from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate


def create_feedback(db: Session, payload: FeedbackCreate) -> Feedback:
    feedback = Feedback(**payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def list_feedback(db: Session, session_id: str | None = None) -> list[Feedback]:
    query = db.query(Feedback)
    if session_id:
        query = query.filter(Feedback.session_id == session_id)
    return query.order_by(Feedback.created_at.desc()).all()
