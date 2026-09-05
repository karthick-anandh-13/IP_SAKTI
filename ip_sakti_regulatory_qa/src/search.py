"""
Hybrid retrieval for IP-SAKTI Sahayak — Regulatory Intelligence & QA.

Combines:
  - BM25 keyword search (good for exact legal terms: "Section 3(p)", "Schedule T")
  - Dense vector semantic search (good for paraphrased / multilingual queries)

This is the module the team's generation/RAG component should call to get
retrieved passages + citation metadata before passing them to the LLM.

Run directly for a quick manual test:
    python src/search.py "can I patent a traditional ayurvedic formulation in india"
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

import config

_model = None  # lazy-loaded singleton so repeated calls don't reload the model


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    return _model


def hybrid_search(query: str, top_k: int = None, jurisdiction: str = None, es: Elasticsearch = None):
    """
    Run a hybrid BM25 + kNN search against the regulatory index.

    Args:
        query: natural-language question (any supported language).
        top_k: number of results to return (defaults to config.TOP_K).
        jurisdiction: optional filter, e.g. "India", "European Union".
        es: optional existing Elasticsearch client (created if not passed).

    Returns:
        List of result dicts with score, text, and citation metadata,
        ordered by relevance (highest first).
    """
    top_k = top_k or config.TOP_K
    es = es or Elasticsearch(config.ES_HOST)
    model = get_model()

    query_vector = model.encode(query, normalize_embeddings=True).tolist()

    filters = []
    if jurisdiction:
        filters.append({"term": {"jurisdiction": jurisdiction}})

    body = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["text^1.0", "title^1.5"],
                            "boost": config.BM25_WEIGHT,
                        }
                    }
                ],
                "filter": filters,
            }
        },
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": max(50, top_k * 10),
            "boost": config.VECTOR_WEIGHT,
            "filter": filters if filters else None,
        },
    }

    response = es.search(index=config.INDEX_NAME, body=body)

    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "score": hit["_score"],
            "text": source["text"],
            "doc_id": source["doc_id"],
            "chunk_id": source["chunk_id"],
            "title": source["title"],
            "jurisdiction": source["jurisdiction"],
            "doc_type": source["doc_type"],
            "source_authority": source["source_authority"],
            "date": source["date"],
            "url": source["url"],
        })
    return results


def format_with_citations(results):
    """Format results as an LLM-ready context block with inline citation tags."""
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(
            f"[{i}] ({r['jurisdiction']} — {r['source_authority']}, {r['date']})\n"
            f"{r['text']}\n"
            f"Source: {r['title']} | {r['url']}\n"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "can I patent a traditional ayurvedic formulation in india"
    print(f"Query: {query}\n")
    results = hybrid_search(query)
    print(format_with_citations(results))
