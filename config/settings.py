"""
Central configuration for IP-SAKTI Sahayak Data Engineering module.
All paths, model names, and DB settings are defined here so the rest
of the pipeline never hardcodes values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---- Base paths ----
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
EMBEDDINGS_DIR = BASE_DIR / "data" / "embeddings"

for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EMBEDDINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---- OCR settings ----
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
# Tesseract language packs needed: eng, hin, tam, san (install via apt/tesseract-lang)
OCR_LANGUAGES = "eng+hin+tam+san"
OCR_CONFIDENCE_THRESHOLD = 60  # below this, flag page for manual review

# ---- Chunking settings ----
MAX_CHUNK_TOKENS = 350
CHUNK_OVERLAP_TOKENS = 40

# ---- Embedding model ----
# multilingual model - handles English, Hindi, Tamil, and reasonably
# handles transliterated Sanskrit terms
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIM = 768

# ---- Database (PostgreSQL + pgvector) ----
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ipsakti")
DB_USER = os.getenv("DB_USER", "ipsakti_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ---- Allowed jurisdictions (used for metadata validation) ----
JURISDICTIONS = [
    "India-AYUSH", "India-BiologicalDiversityAct", "India-DrugsAndCosmeticsAct",
    "India-PatentOffice", "India-TKDL", "WIPO", "EPO", "USPTO", "NagoyaProtocol",
]
