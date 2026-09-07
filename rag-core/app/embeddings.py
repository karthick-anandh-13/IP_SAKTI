"""
Multilingual embedding layer.

Uses a sentence-transformers model trained across 50+ languages (including
Hindi, Tamil, and reasonably transliterated Sanskrit) so that a query typed
in any supported Indian language lands close, in vector space, to source
passages that may themselves be in English, Hindi, or Sanskrit.

In production this is the natural slot to instead call a Bhashini-fine-tuned
encoder; the LangChain `Embeddings` interface keeps that swap a one-line change.
"""
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from app.config import get_settings


class MultilingualEmbeddings(Embeddings):
    """LangChain-compatible wrapper around a multilingual SentenceTransformer."""

    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self._model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        vector = self._model.encode(
            [text], normalize_embeddings=True, show_progress_bar=False
        )[0]
        return vector.tolist()


@lru_cache
def get_embedder() -> MultilingualEmbeddings:
    """Singleton so the (heavy) model is loaded once per process."""
    return MultilingualEmbeddings()
