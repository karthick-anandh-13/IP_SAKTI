from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.feedback import service
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)) -> FeedbackOut:
    feedback = service.create_feedback(db, payload)
    return FeedbackOut.model_validate(feedback)


@router.get("", response_model=list[FeedbackOut])
def list_feedback(
    session_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[FeedbackOut]:
    feedback_items = service.list_feedback(db, session_id)
    return [FeedbackOut.model_validate(f) for f in feedback_items]
