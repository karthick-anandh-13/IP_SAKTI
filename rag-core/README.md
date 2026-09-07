# IP-SAKTI Sahayak — AI RAG Core & Architecture (Prototype)

This is the **RAG Core & Architecture** module (Python / FastAPI / LangChain / Qdrant)
for IP-SAKTI Sahayak — a multilingual, source-cited AI assistant for Intellectual
Property and regulatory guidance in Ayurveda.

It implements the three pillars from the project brief:

1. **Grounded retrieval, not generation from memory** — every answer is built only
   from passages retrieved from a Qdrant vector store seeded with statutes,
   regulations, gazette notifications, patent documents, TKDL prior-art records,
   classical texts, and WIPO/EPO/USPTO standards.
2. **Source-cited responses** — every retrieved chunk carries structured metadata
   (jurisdiction, doc type, clause/section, official URL) so each citation is
   traceable and clickable, never a bare "Source 1".
3. **Multilingual input & output** — a multilingual sentence-embedding model
   handles Hindi / Tamil / Sanskrit-transliteration / English queries against
   English/Hindi/Sanskrit source text; the response language mirrors the query
   language by default. A slot is left for wiring in Bhashini's ASR/MT models.

## Architecture

```
Query (any language)
      │
      ▼
[langdetect] ── detect language
      │
      ▼
[MultilingualEmbeddings]  (sentence-transformers, multilingual)
      │  embed_query()
      ▼
[Qdrant]  ── vector search + jurisdiction/doc_type payload filters
      │  top-k ScoredPoints (with full source metadata in payload)
      ▼
[synthesize_answer]
   ├─ "anthropic" mode → Claude, strict "cite every claim" system prompt
   └─ "template" mode  → deterministic extractive assembly (no API key needed)
      │
      ▼
QueryResponse { answer, citations[], disclaimer }
```

```
app/
  config.py       Settings (env-driven): Qdrant mode, embedding model, LLM provider
  schemas.py      SourceDocument / Citation / Query & Ingest request-response models
  embeddings.py   Multilingual embedding wrapper (LangChain Embeddings interface)
  vectorstore.py  Qdrant client, collection setup, filtered similarity search
  ingestion.py    Clause-aware chunking + embed + upsert pipeline
  rag_chain.py    Retrieval orchestration + grounded, cited answer synthesis
  main.py         FastAPI app: /health, /ingest, /query, /collection/stats
data/
  sample_docs.json   Seed corpus: Patents Act §3(d), TKDL turmeric prior art,
                      AYUSH gazette notification, WIPO TK provisions, EPO
                      examination guidelines, Biological Diversity Act §6
scripts/
  ingest_sample_data.py  One-shot script to seed the sample corpus
```

## Why these design choices

- **Qdrant "local" mode by default** — runs embedded, on-disk, with zero
  infrastructure, so the prototype boots with just `pip install`. Flip
  `QDRANT_MODE=server` + `QDRANT_URL` to point at a real Qdrant deployment
  (Docker / Qdrant Cloud) for production without touching any other code.
- **`LLM_PROVIDER=template` fallback** — the extractive synthesizer needs no
  API key and produces a fully cited answer straight from retrieved text,
  so retrieval quality can be demoed/graded independently of any LLM cost.
  Switch to `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` for fluent,
  Claude-synthesized answers under a strict "only cite retrieved context"
  system prompt.
- **Clause-aware chunking** — legal/statutory text is split with generous
  chunk size (800 chars) and overlap (120 chars) so a clause like "Section
  3(d)" is unlikely to be torn across chunk boundaries, which would corrupt
  a citation.
- **Metadata lives in the Qdrant payload itself** — no separate lookup table;
  a retrieved point is immediately convertible into a `Citation` with a
  clickable `official_url`.
- **`score_threshold`** — queries with no confident match return an explicit
  "not found in verified sources" message instead of letting the LLM guess,
  which is the core anti-hallucination guarantee for a legal-guidance tool.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit as needed (LLM_PROVIDER, ANTHROPIC_API_KEY, etc.)
```

Seed the sample knowledge base:

```bash
python -m scripts.ingest_sample_data
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

## Example usage

**Ingest a new document** (e.g. a fresh gazette notification):

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "doc_id": "IN-AYUSH-GAZ-2024-07",
      "title": "AYUSH GMP Amendment",
      "doc_type": "gazette_notification",
      "jurisdiction": "IN",
      "clause_or_section": "Schedule T, Rule 4",
      "issuing_authority": "Ministry of AYUSH",
      "official_url": "https://www.ayush.gov.in/",
      "language": "en",
      "text": "..."
    }]
  }'
```

**Query in Hindi:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "हल्दी को भारत में पेटेंट कराने के लिए कौन सी बाधाएं हैं?"}'
```

**Query in English with jurisdiction filter:**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What approval is needed before patenting an invention based on an Indian biological resource?",
    "jurisdiction_filter": "IN"
  }'
```

Response shape:

```json
{
  "query": "...",
  "detected_language": "en",
  "answer": "...(cited with [1], [2]...)",
  "citations": [
    {
      "doc_id": "IN-BDACT-2002-S6#chunk0",
      "title": "Biological Diversity Act, 2002 — Section 6",
      "doc_type": "statute",
      "jurisdiction": "IN",
      "clause_or_section": "Section 6",
      "official_url": "https://nbaindia.gov.in/",
      "relevance_score": 0.81,
      "snippet": "No person shall apply for any intellectual property right..."
    }
  ],
  "disclaimer": "This is AI-generated guidance for informational purposes only..."
}
```

## Integration points for the rest of the team

- **Frontend / multilingual I/O team**: call `/query` with raw user text in
  any supported language; `detected_language` tells you what was typed so
  you can route ASR/TTS via Bhashini if the input arrived as speech.
- **Data/legal team**: populate `data/` (or call `/ingest` directly) with more
  `SourceDocument` records — the schema is the contract. `doc_type` and
  `jurisdiction` enums in `app/schemas.py` are the two dimensions currently
  filterable at query time; extend them there first if new categories arise.
- **Ops**: switch `QDRANT_MODE=server` and point `QDRANT_URL` at a managed
  Qdrant instance before deploying beyond a laptop demo.

## Verified in this environment

Ingestion, chunking, Qdrant filtering/search, and the template (no-API-key)
citation-synthesis path were exercised end-to-end here with a stub embedder
(to avoid a large model download in this sandbox); all wiring — schema
validation, clause-aware chunking, payload-filtered retrieval, and cited
answer assembly — passed. Swap in the real `sentence-transformers` model
(already pinned in `requirements.txt`) on first run in your own environment
to get genuine multilingual semantic retrieval.
