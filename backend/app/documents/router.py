from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.documents import service
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentOut

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(
    jurisdiction: str | None = Query(default=None),
    category: str | None = Query(default=None),
    language: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DocumentOut]:
    documents = service.list_documents(db, jurisdiction, category, language)
    return [DocumentOut.model_validate(d) for d in documents]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentOut:
    document = service.create_document(db, payload)
    return DocumentOut.model_validate(document)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)) -> DocumentOut:
    document = service.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentOut.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = service.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
