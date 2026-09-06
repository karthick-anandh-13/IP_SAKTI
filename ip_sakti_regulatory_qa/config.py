"""
Central configuration for IP-SAKTI Sahayak — Regulatory Intelligence & QA module.
Edit these values as your setup changes (e.g. if you move to Elastic Cloud later).
"""

# --- Elasticsearch connection ---
ES_HOST = "http://localhost:9200"
INDEX_NAME = "ip_sakti_regulatory_docs"

# --- Embedding model ---
# Multilingual model so the RAG pipeline can handle queries in English, Hindi,
# Tamil, etc. — important since the project promises multilingual support.
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIM = 768

# --- Chunking ---
CHUNK_SIZE_WORDS = 180       # words per chunk
CHUNK_OVERLAP_WORDS = 40     # overlap between consecutive chunks

# --- Retrieval ---
TOP_K = 5                    # number of chunks retrieved per query
BM25_WEIGHT = 0.4            # weight given to keyword (BM25) score in hybrid search
VECTOR_WEIGHT = 0.6          # weight given to dense vector (semantic) score
