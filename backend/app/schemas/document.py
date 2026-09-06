from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    jurisdiction: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=120)
    language: str = Field(default="en", max_length=10)
    source_url: str | None = Field(default=None, max_length=1000)


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    jurisdiction: str
    category: str
    language: str
    source_url: str | None
    uploaded_at: datetime
