from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    language: str = Field(default="en", max_length=10)
    session_id: str | None = None
