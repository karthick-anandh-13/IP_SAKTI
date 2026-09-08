import requests

from app.novelty.schemas import (
    NoveltyScanRequest,
    NoveltyScanResponse,
    PriorArtMatch,
)


RAG_CORE_URL = "http://127.0.0.1:8001"


def scan_novelty(request: NoveltyScanRequest) -> NoveltyScanResponse:
    """
    Search the existing RAG Core for records related to the invention
    and convert the retrieval results into a prior-art risk assessment.
    """

    response = requests.post(
        f"{RAG_CORE_URL}/query",
        json={
            "query": request.invention,
            "top_k": request.top_k,
        },
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()

    matches = []

    for citation in data.get("citations", []):
        matches.append(
            PriorArtMatch(
                doc_id=citation["doc_id"],
                title=citation["title"],
                source_type=citation["doc_type"],
                jurisdiction=citation["jurisdiction"],
                similarity=citation["relevance_score"],
                clause_or_section=citation.get("clause_or_section"),
                official_url=citation.get("official_url"),
                snippet=citation["snippet"],
            )
        )

    risk_score = _calculate_risk_score(matches)
    risk_level = _get_risk_level(risk_score)
    summary = _build_summary(risk_level, matches)

    return NoveltyScanResponse(
        invention=request.invention,
        risk_level=risk_level,
        risk_score=risk_score,
        summary=summary,
        matches=matches,
    )


def _calculate_risk_score(matches: list[PriorArtMatch]) -> float:
    """
    Calculate a simple prior-art risk score from the strongest matches.

    The score is based on the highest similarity found in the retrieved
    prior-art records.
    """

    if not matches:
        return 0.0

    highest_similarity = max(match.similarity for match in matches)

    return round(min(max(highest_similarity, 0.0), 1.0), 4)


def _get_risk_level(score: float) -> str:
    if score >= 0.80:
        return "HIGH"
    if score >= 0.60:
        return "MEDIUM"
    return "LOW"


def _build_summary(
    risk_level: str,
    matches: list[PriorArtMatch],
) -> str:
    if not matches:
        return (
            "No closely matching prior-art records were retrieved. "
            "This does not establish that the invention is novel."
        )

    strongest = matches[0]

    return (
        f"{risk_level} prior-art risk. "
        f"The search retrieved {len(matches)} potentially relevant record(s). "
        f"The strongest match is '{strongest.title}' with a similarity score "
        f"of {strongest.similarity:.4f}. "
        "Review the cited source and underlying document before making any "
        "patentability decision."
    )