"""
embeddings.py
-------------
Multilingual sentence embeddings for RAG retrieval (Qdrant) in
IP-SAKTI Sahayak.

IMPORTANT INTEGRATION NOTE for the team:
  Whatever embedding model is used HERE to embed a user's query must
  be the SAME model used by the Data Engineering module (#4) to embed
  the regulatory/IP source documents that were pushed into Qdrant.
  Mixing embedding models will silently break retrieval (vectors won't
  be comparable). Confirm the model name with teammate 4 / teammate 1
  and set EMBEDDING_MODEL_NAME below (or pass model_name=... explicitly)
  to match.

Default model: sentence-transformers/LaBSE
  - 109 languages, strong support for Indic scripts, 768-dim output,
    well suited to cross-lingual retrieval (query in Hindi/Tamil/etc.
    matching English-language regulatory documents, or vice versa).

Alternative: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
  - Also solid for multilingual semantic search, slightly smaller.
"""

from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "sentence-transformers/LaBSE"


class MultilingualEmbedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, device: str | None = None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, texts: List[str] | str, normalize: bool = True) -> np.ndarray:
        """
        Embed one string or a list of strings.
        Returns a single 1D vector for a single string input, or a
        2D array (n_texts x dim) for a list input.
        Vectors are L2-normalized by default, which is what Qdrant's
        cosine-distance collections expect.
        """
        single_input = isinstance(texts, str)
        batch = [texts] if single_input else list(texts)

        vectors = self.model.encode(
            batch,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors[0] if single_input else vectors

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()


@lru_cache(maxsize=1)
def get_default_embedder() -> MultilingualEmbedder:
    """Process-wide singleton so the FastAPI backend doesn't reload
    the model on every request."""
    return MultilingualEmbedder()


if __name__ == "__main__":
    emb = get_default_embedder()
    vec = emb.embed("What is the patent registration process for Ayurvedic medicines?")
    print("Embedding dim:", emb.dimension)
    print("First 8 values:", vec[:8])
