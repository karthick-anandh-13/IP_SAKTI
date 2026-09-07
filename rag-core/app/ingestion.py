"""
Ingestion pipeline: takes full SourceDocument records (a whole statute section,
gazette notification, patent claim set, or classical-text passage) and splits
them into retrieval-sized chunks while *preserving every citation field* on
each chunk, then embeds and upserts them into Qdrant.

Legal/statutory text is chunked more conservatively (larger, clause-aware)
than free-form prose, since splitting mid-clause would break citation
integrity -- you never want to cite "half of Section 3(d)".
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.embeddings import get_embedder
from app.schemas import IngestResponse, SourceDocument
from app.vectorstore import upsert_documents

_LEGAL_SEPARATORS = ["\n\n", "\n", ". ", "; ", " "]

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=_LEGAL_SEPARATORS,
)


def chunk_document(doc: SourceDocument) -> list[SourceDocument]:
    """Split one source document's text into overlapping chunks, cloning metadata."""
    pieces = _splitter.split_text(doc.text)
    if len(pieces) <= 1:
        return [doc]

    chunks = []
    for i, piece in enumerate(pieces):
        chunk = doc.model_copy(
            update={
                "doc_id": f"{doc.doc_id}#chunk{i}",
                "text": piece,
                "extra": {**doc.extra, "parent_doc_id": doc.doc_id, "chunk_index": i},
            }
        )
        chunks.append(chunk)
    return chunks


def ingest_documents(documents: list[SourceDocument]) -> IngestResponse:
    from app.config import get_settings

    all_chunks: list[SourceDocument] = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))

    embedder = get_embedder()
    vectors = embedder.embed_documents([c.text for c in all_chunks])
    n = upsert_documents(all_chunks, vectors)

    return IngestResponse(ingested_chunks=n, collection=get_settings().qdrant_collection)
