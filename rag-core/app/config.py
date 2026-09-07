"""
Central configuration for IP-SAKTI Sahayak RAG core.
All values are overridable via environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Qdrant ---
    qdrant_mode: str = "local"                 # "local" | "server"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_local_path: str = "./qdrant_storage"
    qdrant_collection: str = "ip_sakti_kb"

    # --- Embeddings ---
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embedding_dim: int = 768

    # --- LLM synthesis ---
    llm_provider: str = "template"             # "template" | "anthropic"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Retrieval ---
    top_k: int = 5
    score_threshold: float = 0.30

    # --- Multilingual ---
    bhashini_api_key: str | None = None
    bhashini_endpoint: str | None = None
    default_response_language: str = "auto"


@lru_cache
def get_settings() -> Settings:
    return Settings()
