"""
Pydantic data contracts shared across ingestion, retrieval and the API layer.

Design note: every SourceDocument carries enough structured metadata
(instrument type, jurisdiction, clause/section, official URL) that a citation
can be rendered as a clickable, traceable reference -- never just "Source 1".
"""
from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class DocType(str, Enum):
    STATUTE = "statute"                 # e.g. Patents Act 1970, Biological Diversity Act
    REGULATION = "regulation"           # AYUSH / CDSCO regulatory guidelines
    GAZETTE = "gazette_notification"
    PATENT = "patent_document"          # granted patent / application
    PRIOR_ART = "prior_art"             # TKDL entries, classical texts cited as prior art
    CLASSICAL_TEXT = "classical_text"   # Charaka Samhita, Sushruta Samhita, etc.
    INTL_STANDARD = "international_standard"  # WIPO, EPO, USPTO guidelines/rules
    CASE_LAW = "case_law"


class Jurisdiction(str, Enum):
    INDIA = "IN"
    WIPO = "WIPO"
    EPO = "EPO"
    USPTO = "US"
    OTHER = "OTHER"


class SourceDocument(BaseModel):
    """Canonical unit stored in Qdrant payload + used for citation rendering."""

    doc_id: str = Field(..., description="Stable unique ID, e.g. 'IN-PATACT-1970-S3D'")
    title: str
    doc_type: DocType
    jurisdiction: Jurisdiction
    clause_or_section: Optional[str] = Field(
        None, description="e.g. 'Section 3(d)', 'Rule 12(1)(a)', 'Article 27.3(b)'"
    )
    issuing_authority: Optional[str] = Field(
        None, description="e.g. 'Ministry of AYUSH', 'WIPO', 'Indian Patent Office'"
    )
    publication_date: Optional[date] = None
    official_url: Optional[HttpUrl] = Field(
        None, description="Deep link to the gazette/patent/statute page for click-through citation"
    )
    language: str = Field("en", description="ISO 639-1/2 code of the source text")
    text: str = Field(..., description="Chunked passage text actually embedded/retrieved")
    extra: dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    documents: list[SourceDocument]


class IngestResponse(BaseModel):
    ingested_chunks: int
    collection: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, examples=["हल्दी पेटेंट के लिए पूर्व कला क्या है?"])
    top_k: Optional[int] = None
    jurisdiction_filter: Optional[Jurisdiction] = None
    doc_type_filter: Optional[DocType] = None
    response_language: Optional[str] = Field(
        None, description="Force output language (ISO code). Defaults to query language."
    )


class Citation(BaseModel):
    doc_id: str
    title: str
    doc_type: DocType
    jurisdiction: Jurisdiction
    clause_or_section: Optional[str] = None
    official_url: Optional[HttpUrl] = None
    relevance_score: float
    snippet: str


class QueryResponse(BaseModel):
    query: str
    detected_language: str
    answer: str
    citations: list[Citation]
    disclaimer: str = (
        "This is AI-generated guidance for informational purposes only and does not "
        "constitute legal advice. Verify all citations against the linked official sources."
    )
