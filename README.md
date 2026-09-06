# IP-SAKTI Sahayak — Data Engineering Module

This module is the ingestion pipeline that turns raw legal, patent, and
Ayurvedic regulatory documents into clean, chunked, embedded vectors
stored in PostgreSQL (pgvector), ready for the RAG retrieval layer.

## Pipeline stages

```
Raw PDF (data/raw/)
      │
      ▼
1. OCR fallback (src/ocr_processor.py)
   - Uses PyMuPDF's native text layer where possible
   - Falls back to Tesseract OCR (eng+hin+tam+san) for scanned pages
   - Flags low-confidence pages for manual review
      │
      ▼
2. Structured extraction (src/pdf_extractor.py)
   - Detects section/clause boundaries (Section, Rule, Article, 3.2.1, (a), etc.)
   - Extracts tables (Schedule T classifications, GI registers, etc.)
      │
      ▼
3. Cleaning + clause-aware chunking (src/cleaner_chunker.py)
   - Strips OCR noise, page numbers, irregular whitespace
   - Chunks by sentence boundary, respects max token limit + overlap
   - Detects chunk language (en/hi/ta/sa)
      │
      ▼
4. Multilingual embeddings (src/embedder.py)
   - sentence-transformers/paraphrase-multilingual-mpnet-base-v2
   - Handles English, Hindi, Tamil, transliterated Sanskrit
      │
      ▼
5. Storage (src/db.py)
   - PostgreSQL + pgvector
   - documents table: metadata for citations (source, jurisdiction, act name, URL)
   - chunks table: text + embedding + section reference
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# System dependency for OCR:
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tam tesseract-ocr-san

cp .env.example .env   # fill in your DB credentials
```

## Running the pipeline on a single document

```bash
python -m src.pipeline \
  --file data/raw/ayush_gazette_2023.pdf \
  --jurisdiction India-AYUSH \
  --source-type gazette \
  --title "AYUSH Notification 2023" \
  --act-name "Drugs and Cosmetics Act - Schedule T" \
  --source-url "https://ayush.gov.in/..." \
  --doc-id ayush_2023_001
```

## Running tests

```bash
pytest tests/
```

## Metadata schema

Every chunk carries `doc_id`, `page_number`, `section_or_clause`, and
`language`, and every document carries `jurisdiction`, `source_type`,
`act_or_regulation_name`, and `source_url`. This is what lets the RAG
layer generate clickable, traceable citations instead of hallucinated
references.

Supported jurisdictions (see `config/settings.py`):
India-AYUSH, India-BiologicalDiversityAct, India-DrugsAndCosmeticsAct,
India-PatentOffice, India-TKDL, WIPO, EPO, USPTO, NagoyaProtocol.

## Notes for the team

- Raw source PDFs are **not** committed to this repo (see `.gitignore`) —
  many come from restricted/rate-limited government portals. Only the
  pipeline code is versioned.
- `db.init_db()` creates the `vector` extension and tables automatically
  on first run — needs a Postgres instance with pgvector installed.
- Embedding model loads lazily and is cached as a singleton across calls
  in the same process (see `src/embedder.py`).
