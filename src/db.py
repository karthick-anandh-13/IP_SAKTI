"""
Database layer.
Stores document metadata and embedded chunks in PostgreSQL using
pgvector for similarity search. This is what the backend/RAG team's
FastAPI service will query at inference time.
"""

import logging
from typing import List

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Date, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

from config.settings import DATABASE_URL, EMBEDDING_DIM
from src.schema import DocumentMetadata, EmbeddedChunk

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class DocumentORM(Base):
    __tablename__ = "documents"

    doc_id = Column(String, primary_key=True)
    title = Column(Text)
    jurisdiction = Column(String, index=True)
    source_type = Column(String)
    source_url = Column(Text, nullable=True)
    act_or_regulation_name = Column(Text, nullable=True)
    publication_date = Column(Date, nullable=True)
    language = Column(String)
    file_path = Column(Text)
    ocr_used = Column(Boolean, default=False)
    ocr_confidence = Column(Float, nullable=True)


class ChunkORM(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    doc_id = Column(String, index=True)
    page_number = Column(Integer, nullable=True)
    section_or_clause = Column(Text, nullable=True)
    text = Column(Text)
    token_count = Column(Integer)
    language = Column(String)
    embedding = Column(Vector(EMBEDDING_DIM))
    embedding_model = Column(String)


def init_db():
    """Creates tables (and pgvector extension) if they don't exist."""
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
    Base.metadata.create_all(engine)
    logger.info("Database initialised.")


def save_document_metadata(meta: DocumentMetadata):
    session = SessionLocal()
    try:
        record = DocumentORM(**meta.model_dump())
        session.merge(record)  # merge = upsert on primary key
        session.commit()
    finally:
        session.close()


def save_chunks(chunks: List[EmbeddedChunk]):
    session = SessionLocal()
    try:
        for chunk in chunks:
            record = ChunkORM(**chunk.model_dump())
            session.merge(record)
        session.commit()
        logger.info("Saved %d chunks to DB", len(chunks))
    finally:
        session.close()


def similarity_search(query_embedding: List[float], jurisdiction: str = None, top_k: int = 5):
    """
    Basic vector similarity search - used by the RAG retrieval layer.
    Filters by jurisdiction if provided (e.g. only "India-AYUSH" results).
    """
    session = SessionLocal()
    try:
        query = session.query(ChunkORM)
        if jurisdiction:
            query = query.join(DocumentORM, ChunkORM.doc_id == DocumentORM.doc_id)
            query = query.filter(DocumentORM.jurisdiction == jurisdiction)

        results = query.order_by(
            ChunkORM.embedding.cosine_distance(query_embedding)
        ).limit(top_k).all()

        return results
    finally:
        session.close()
