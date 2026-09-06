"""
Embedding generation module.
Uses a multilingual sentence-transformer so English, Hindi, Tamil, and
transliterated Sanskrit queries can all be embedded into the same
vector space for retrieval.
"""

import logging
from typing import List

from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL_NAME
from src.schema import TextChunk, EmbeddedChunk

logger = logging.getLogger(__name__)

_model = None  # lazy-loaded singleton, avoids reloading the model per call


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_chunks(chunks: List[TextChunk], batch_size: int = 32) -> List[EmbeddedChunk]:
    """
    Generates embeddings for a list of TextChunks in batches.
    Returns EmbeddedChunk objects ready for storage in pgvector.
    """
    model = get_model()
    texts = [c.text for c in chunks]

    logger.info("Embedding %d chunks in batches of %d", len(texts), batch_size)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    embedded_chunks = []
    for chunk, vector in zip(chunks, vectors):
        embedded_chunks.append(
            EmbeddedChunk(
                **chunk.model_dump(),
                embedding=vector.tolist(),
                embedding_model=EMBEDDING_MODEL_NAME,
            )
        )

    return embedded_chunks
