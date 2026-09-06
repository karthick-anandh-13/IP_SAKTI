"""
Shared data models for the ingestion pipeline.
Every extracted chunk carries this metadata so the RAG layer can
build clickable, traceable citations later.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    doc_id: str = Field(..., description="Unique ID for the source document")
    title: str
    jurisdiction: str = Field(..., description="e.g. India-AYUSH, WIPO, USPTO")
    source_type: str = Field(..., description="gazette | patent | statute | guideline | classical_text")
    source_url: Optional[str] = None
    act_or_regulation_name: Optional[str] = None
    section_or_clause: Optional[str] = None
    publication_date: Optional[date] = None
    language: str = "en"
    file_path: str
    ocr_used: bool = False
    ocr_confidence: Optional[float] = None


class TextChunk(BaseModel):
    chunk_id: str
    doc_id: str
    page_number: Optional[int] = None
    section_or_clause: Optional[str] = None
    text: str
    token_count: int
    language: str = "en"


class EmbeddedChunk(TextChunk):
    embedding: list[float]
    embedding_model: str
