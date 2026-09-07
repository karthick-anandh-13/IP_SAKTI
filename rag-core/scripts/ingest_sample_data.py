"""
Seed the Qdrant collection with the bundled sample dataset.

Usage:
    python -m scripts.ingest_sample_data
"""
import json
from pathlib import Path

from app.ingestion import ingest_documents
from app.schemas import SourceDocument

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_docs.json"


def main() -> None:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    documents = [SourceDocument(**d) for d in raw]
    result = ingest_documents(documents)
    print(f"Ingested {result.ingested_chunks} chunks into collection '{result.collection}'.")


if __name__ == "__main__":
    main()
