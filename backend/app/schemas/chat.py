from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)
    language: str = Field(default="en", max_length=10)


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    language: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    sender: Literal["user", "assistant"]
    message: str = Field(min_length=1)
    source_citation: str | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    sender: str
    message: str
    source_citation: str | None
    timestamp: datetime


class ChatSessionDetailOut(ChatSessionOut):
    messages: list[ChatMessageOut] = []
