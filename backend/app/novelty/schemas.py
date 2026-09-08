from pydantic import BaseModel, Field
from typing import Optional


class NoveltyScanRequest(BaseModel):
    invention: str = Field(
        ...,
        min_length=10,
        description="Description of the invention or formulation to be checked for prior art.",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of prior-art records to retrieve.",
    )


class PriorArtMatch(BaseModel):
    doc_id: str
    title: str
    source_type: str
    jurisdiction: str
    similarity: float
    clause_or_section: Optional[str] = None
    official_url: Optional[str] = None
    snippet: str


class NoveltyScanResponse(BaseModel):
    invention: str
    risk_level: str
    risk_score: float
    summary: str
    matches: list[PriorArtMatch]