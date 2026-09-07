"""
Qdrant vector store layer.

Two run modes so the prototype works with zero infra:
  - "local": embedded Qdrant persisted to disk at QDRANT_LOCAL_PATH (no server needed)
  - "server": talks to a real Qdrant instance (docker / Qdrant Cloud) via QDRANT_URL

Every point's payload stores the FULL SourceDocument metadata so a retrieved
hit can be turned directly into a clickable Citation without a second lookup.
"""
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings
from app.schemas import DocType, Jurisdiction, SourceDocument


@lru_cache
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    if settings.qdrant_mode == "server":
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    # embedded / on-disk mode -- great for a prototype, no server to run
    return QdrantClient(path=settings.qdrant_local_path)


def ensure_collection() -> None:
    settings = get_settings()
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection in existing:
        return
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=qmodels.VectorParams(
            size=settings.embedding_dim,
            distance=qmodels.Distance.COSINE,
        ),
    )
    # Payload indexes speed up the jurisdiction / doc_type filters used at query time
    for field in ("jurisdiction", "doc_type", "language"):
        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name=field,
            field_schema=qmodels.PayloadSchemaType.KEYWORD,
        )


def upsert_documents(chunks: list[SourceDocument], vectors: list[list[float]]) -> int:
    settings = get_settings()
    ensure_collection()
    client = get_qdrant_client()

    points = [
        qmodels.PointStruct(
            id=_stable_point_id(chunk.doc_id, idx),
            vector=vector,
            payload=chunk.model_dump(mode="json"),
        )
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def _stable_point_id(doc_id: str, salt: int) -> str:
    import hashlib

    return hashlib.sha256(f"{doc_id}-{salt}".encode()).hexdigest()[:32]


def build_filter(
    jurisdiction: Jurisdiction | None, doc_type: DocType | None
) -> qmodels.Filter | None:
    conditions = []
    if jurisdiction:
        conditions.append(
            qmodels.FieldCondition(
                key="jurisdiction", match=qmodels.MatchValue(value=jurisdiction.value)
            )
        )
    if doc_type:
        conditions.append(
            qmodels.FieldCondition(
                key="doc_type", match=qmodels.MatchValue(value=doc_type.value)
            )
        )
    return qmodels.Filter(must=conditions) if conditions else None


def search(
    query_vector: list[float],
    top_k: int,
    score_threshold: float,
    qfilter: qmodels.Filter | None = None,
) -> list[qmodels.ScoredPoint]:
    """Wraps the modern `query_points` API (qdrant-client >= 1.10) but returns
    the flat list of scored points, matching the older `search()` shape, so
    callers elsewhere in this codebase don't need to know about the change."""
    settings = get_settings()
    client = get_qdrant_client()
    result = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
        query_filter=qfilter,
        with_payload=True,
    )
    return result.points
