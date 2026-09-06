from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    session_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    rating: int
    comment: str | None
    created_at: datetime
