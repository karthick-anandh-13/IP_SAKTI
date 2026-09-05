"""
Ingestion pipeline for IP-SAKTI Sahayak — Regulatory Intelligence & QA.

Responsibilities:
1. Load raw regulatory/IP documents (data/sample_documents.json for now;
   swap in your real scraped/collected corpus later — same schema).
2. Chunk long documents into overlapping passages so retrieval is precise
   and citations point to a specific passage, not a whole 5-page document.
3. Generate multilingual embeddings for each chunk.
4. Create an Elasticsearch index with a hybrid mapping (BM25 text fields +
   dense_vector field) and bulk-index all chunks.

Run:
    python src/ingest.py
"""

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import config


def load_documents(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Simple word-based sliding-window chunker."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def build_chunk_records(documents):
    """Turn each document into one or more chunk records ready for indexing."""
    records = []
    for doc in documents:
        chunks = chunk_text(doc["text"], config.CHUNK_SIZE_WORDS, config.CHUNK_OVERLAP_WORDS)
        for i, chunk in enumerate(chunks):
            records.append({
                "doc_id": doc["id"],
                "chunk_id": f"{doc['id']}::chunk{i}",
                "title": doc["title"],
                "jurisdiction": doc["jurisdiction"],
                "doc_type": doc["doc_type"],
                "source_authority": doc["source_authority"],
                "date": doc["date"],
                "url": doc.get("url", ""),
                "chunk_index": i,
                "text": chunk,
            })
    return records


def create_index(es: Elasticsearch, index_name: str, dim: int):
    if es.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Deleting and recreating for a clean run.")
        es.indices.delete(index=index_name)

    mapping = {
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "chunk_id": {"type": "keyword"},
                "title": {"type": "text"},
                "jurisdiction": {"type": "keyword"},
                "doc_type": {"type": "keyword"},
                "source_authority": {"type": "text"},
                "date": {"type": "date", "ignore_malformed": True},
                "url": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "text": {"type": "text"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": dim,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        }
    }
    es.indices.create(index=index_name, body=mapping)
    print(f"Created index '{index_name}'.")


def index_records(es: Elasticsearch, index_name: str, records, model: SentenceTransformer):
    print(f"Embedding {len(records)} chunks with '{config.EMBEDDING_MODEL_NAME}'...")
    texts = [r["text"] for r in records]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    actions = []
    for record, embedding in zip(records, embeddings):
        record_with_vector = dict(record)
        record_with_vector["embedding"] = embedding.tolist()
        actions.append({
            "_index": index_name,
            "_id": record["chunk_id"],
            "_source": record_with_vector,
        })

    print("Bulk indexing into Elasticsearch...")
    helpers.bulk(es, actions)
    es.indices.refresh(index=index_name)
    print(f"Indexed {len(actions)} chunks into '{index_name}'.")


def main():
    es = Elasticsearch(config.ES_HOST)
    if not es.ping():
        raise ConnectionError(
            f"Could not connect to Elasticsearch at {config.ES_HOST}. "
            f"Make sure it's running (docker-compose up -d)."
        )

    docs_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "sample_documents.json",
    )
    documents = load_documents(docs_path)
    print(f"Loaded {len(documents)} source documents.")

    records = build_chunk_records(documents)
    print(f"Split into {len(records)} chunks (chunk_size={config.CHUNK_SIZE_WORDS} words, "
          f"overlap={config.CHUNK_OVERLAP_WORDS} words).")

    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

    create_index(es, config.INDEX_NAME, config.EMBEDDING_DIM)
    index_records(es, config.INDEX_NAME, records, model)


if __name__ == "__main__":
    main()
