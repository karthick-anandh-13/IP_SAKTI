"""
IP-SAKTI Sahayak -- AI RAG Core & Architecture (FastAPI service)

Run:
    uvicorn app.main:app --reload --port 8000

Endpoints:
    GET  /health          liveness check
    POST /ingest           load SourceDocument records into Qdrant
    POST /query             ask a question, get a grounded + cited answer
    GET  /collection/stats  quick counts for the demo/debug UI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.ingestion import ingest_documents
from app.rag_chain import run_query
from app.schemas import IngestRequest, IngestResponse, QueryRequest, QueryResponse
from app.vectorstore import ensure_collection, get_qdrant_client

app = FastAPI(
    title="IP-SAKTI Sahayak — RAG Core",
    description=(
        "Multilingual, source-cited RAG API for Ayurveda IP & regulatory guidance. "
        "Grounded exclusively in ingested legal, patent, and botanical/Ayurvedic records."
    ),
    version="0.1.0",
)

# Prototype-friendly CORS; tighten origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    ensure_collection()


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "qdrant_mode": settings.qdrant_mode,
        "collection": settings.qdrant_collection,
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    if not request.documents:
        raise HTTPException(status_code=400, detail="documents list is empty")
    try:
        return ingest_documents(request.documents)
    except Exception as exc:  # pragma: no cover - prototype-level error surfacing
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    try:
        return run_query(request)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc


@app.get("/collection/stats")
def collection_stats() -> dict:
    settings = get_settings()
    client = get_qdrant_client()
    try:
        info = client.get_collection(settings.qdrant_collection)
        return {
            "collection": settings.qdrant_collection,
            "points_count": info.points_count,
            "status": info.status,
        }
    except Exception:
        return {"collection": settings.qdrant_collection, "points_count": 0, "status": "not_created"}
