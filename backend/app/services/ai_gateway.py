"""
Gateway to the external RAG retrieval + LLM inference service.

This backend does NOT implement retrieval or inference itself — it simply
forwards the incoming question to the RAG service and relays the response
back to the caller unmodified.
"""
import httpx
from fastapi import HTTPException, status

from app.config import settings
from app.schemas.ask import AskRequest


async def forward_question(payload: AskRequest) -> dict:
    """
    POST the incoming question to the RAG/LLM service and return its JSON
    response exactly as received.
    """
    body = {
        "question": payload.question,
        "language": payload.language,
        "session_id": payload.session_id,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.RAG_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(settings.RAG_SERVICE_URL, json=body)
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach the RAG/LLM inference service.",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The RAG/LLM inference service timed out.",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAG service returned an error: {response.status_code} {response.text}",
        )

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="RAG/LLM service returned a non-JSON response.",
        ) from exc
