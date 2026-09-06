from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate


def create_document(db: Session, payload: DocumentCreate) -> Document:
    document = Document(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(
    db: Session,
    jurisdiction: str | None = None,
    category: str | None = None,
    language: str | None = None,
) -> list[Document]:
    query = db.query(Document)
    if jurisdiction:
        query = query.filter(Document.jurisdiction.ilike(jurisdiction))
    if category:
        query = query.filter(Document.category.ilike(category))
    if language:
        query = query.filter(Document.language == language)
    return query.order_by(Document.uploaded_at.desc()).all()


def get_document(db: Session, document_id: str) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def delete_document(db: Session, document_id: str) -> bool:
    document = get_document(db, document_id)
    if not document:
        return False
    db.delete(document)
    db.commit()
    return True
