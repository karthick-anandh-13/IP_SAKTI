# Multilingual NLP Module — IP-SAKTI Sahayak

Component **5. Multilingual NLP** of the IP-SAKTI Sahayak project.

Stack: **IndicTrans2** (translation) + **Sentence-Transformers** (embeddings).

## What this module does

1. **Detect** the language of an incoming user query (any of the 22
   scheduled Indian languages, or English), via `lang_detect.py`.
2. **Translate** non-English queries into English with IndicTrans2
   (`translator.py`), so retrieval and QA can run over the (mostly
   English) regulatory corpus.
3. **Embed** the (English) query with a multilingual Sentence-Transformer
   model (`embeddings.py`), producing the vector that Team 1 passes to
   Qdrant for similarity search.
4. **Localize** the final generated answer back into the user's
   original language, so the assistant replies in the language they
   asked in — with the source citations preserved as-is.

## Files

| File              | Purpose                                                            |
|-------------------|---------------------------------------------------------------------|
| `lang_detect.py`  | Script/Unicode-based language ID -> FLORES-200 code                |
| `translator.py`   | IndicTrans2 wrapper (Indic<->English translation)                  |
| `embeddings.py`   | Multilingual sentence embeddings (LaBSE) for RAG retrieval          |
| `pipeline.py`     | Combines the above into `MultilingualNLPPipeline` — the public API |
| `demo.py`         | Runnable example across Hindi/Tamil/Telugu/English queries          |

## Public API (what the rest of the team calls)

```python
from pipeline import MultilingualNLPPipeline

pipeline = MultilingualNLPPipeline()

# Step 1 - on incoming query:
result = pipeline.process_query(user_query)
# result.detected_lang        -> e.g. "hin_Deva"
# result.english_query        -> normalized English text
# result.query_embedding      -> np.ndarray, pass straight to Qdrant search

# ... Team 1 does Qdrant retrieval with result.query_embedding ...
# ... Team 6 generates `english_answer` from retrieved + cited chunks ...

# Step 2 - on outgoing answer:
final_answer = pipeline.localize_answer(english_answer, result.response_lang)
```

## Setup

```bash
pip install -r requirements.txt
python demo.py
```

The first run downloads the IndicTrans2 distilled 200M checkpoints and
the LaBSE embedding model from HuggingFace (a few GB total). Subsequent
runs use the local HF cache.

## ⚠️ Integration note for Team 1 / Team 4

The query embedding model here (`sentence-transformers/LaBSE`, 768-dim)
**must be the same model** used to embed the source documents that were
indexed in Qdrant. If Data Engineering (#4) embedded documents with a
different model, either:
- point `embeddings.py`'s `EMBEDDING_MODEL_NAME` at that same model, or
- re-embed the document corpus with LaBSE to match this module.

Mismatched embedding models will make cosine similarity meaningless and
silently degrade retrieval quality — please confirm this before wiring
the pipelines together.

## Language coverage

Supports all languages IndicTrans2 covers, including Hindi, Marathi,
Sanskrit, Bengali, Assamese, Punjabi, Gujarati, Odia, Tamil, Telugu,
Kannada, Malayalam and Urdu — relevant given Ayurvedic source texts are
frequently in Sanskrit or regional languages.

**Known limitation:** languages sharing a script (Hindi/Marathi/Sanskrit
in Devanagari; Bengali/Assamese in Bengali script) are disambiguated with
a small keyword heuristic in `lang_detect.py`, not a trained classifier.
For higher accuracy, swap in AI4Bharat's dedicated
[IndicLID](https://github.com/AI4Bharat/IndicLID) model — it's a drop-in
replacement for `detect_language()`, since every other module only
depends on the FLORES-200 code it returns.

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
