from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.chat import service
from app.database import get_db
from app.models.user import User
from app.schemas.ask import AskRequest
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageOut,
    ChatSessionCreate,
    ChatSessionDetailOut,
    ChatSessionOut,
)
from app.services import ai_gateway

router = APIRouter(tags=["Chat"])


@router.post("/chat/session", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionOut:
    session = service.create_session(db, current_user.id, payload)
    return ChatSessionOut.model_validate(session)


@router.get("/chat/sessions", response_model=list[ChatSessionOut])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSessionOut]:
    sessions = service.list_sessions(db, current_user.id)
    return [ChatSessionOut.model_validate(s) for s in sessions]


@router.get("/chat/{session_id}", response_model=ChatSessionDetailOut)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionDetailOut:
    session = service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    return ChatSessionDetailOut.model_validate(session)


@router.post(
    "/chat/{session_id}/message",
    response_model=ChatMessageOut,
    status_code=status.HTTP_201_CREATED,
)
def post_message(
    session_id: str,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatMessageOut:
    session = service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    message = service.add_message(db, session, payload)
    return ChatMessageOut.model_validate(message)


@router.delete("/chat/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = service.delete_session(db, session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")


@router.post("/ask")
async def ask(
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """
    AI Gateway endpoint. Forwards the question to the RAG/LLM inference
    service (POST {RAG_SERVICE_URL}) and returns its JSON response exactly
    as received, with no reshaping.
    """
    raw_response = await ai_gateway.forward_question(payload)
    return JSONResponse(content=raw_response)
