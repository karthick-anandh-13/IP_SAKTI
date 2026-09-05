# IP-SAKTI Sahayak — Regulatory Intelligence & QA Module

This is the **Regulatory Intelligence, Elasticsearch retrieval, and Evaluation**
component of the IP-SAKTI Sahayak project. It is the retrieval half of the
RAG pipeline: it finds the right regulatory/IP passages for a question and
hands them to whoever's building the generation/LLM side, along with
citation metadata, so answers stay source-cited.

## What's in here

```
ip_sakti_regulatory_qa/
├── docker-compose.yml        # Spins up Elasticsearch + Kibana locally
├── requirements.txt
├── config.py                 # All settings in one place
├── data/
│   └── sample_documents.json # 8 sample regulatory/IP docs (India, WIPO, EU, US)
├── eval/
│   └── test_questions.json   # 8 test questions with expected answers
└── src/
    ├── ingest.py              # Chunk -> embed -> index documents into ES
    ├── search.py               # Hybrid BM25 + vector search, with citations
    └── evaluate.py              # Precision@k, Recall@k, MRR, keyword hit rate
```

## Setup (one-time)

1. **Install Docker Desktop** if you don't have it: https://www.docker.com/products/docker-desktop/
2. **Start Elasticsearch:**
   ```bash
   docker-compose up -d
   ```
   Wait ~30 seconds, then check it's alive:
   ```bash
   curl http://localhost:9200
   ```
   You should get a JSON response with cluster info. (Kibana, a visual browser
   for your index, will be at http://localhost:5601 — optional but handy for demos.)

3. **Install Python dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   The first run will download the multilingual embedding model
   (~1GB) — this only happens once.

## Running the pipeline

**Step 1 — Ingest the sample documents:**
```bash
python src/ingest.py
```
This chunks the 8 sample documents, embeds each chunk, and indexes them
into Elasticsearch. You'll see progress bars for embedding and a final
"Indexed N chunks" message.

**Step 2 — Try a search manually:**
```bash
python src/search.py "can I patent a traditional ayurvedic remedy in india"
```
This prints the top 5 retrieved passages with their jurisdiction, source
authority, and URL — exactly the citation metadata your teammates need for
the generation step.

**Step 3 — Run the evaluation:**
```bash
python src/evaluate.py
```
This runs all 8 test questions against the index and prints Precision@k,
Recall@k, Mean Reciprocal Rank, and keyword hit rate — both per-question
and averaged. Save results for your report with:
```bash
python src/evaluate.py --output eval/results.csv
```

## How this fits into the bigger project

- **Your teammates' LLM/generation component** should call
  `hybrid_search(query)` from `src/search.py`, get back a list of cited
  passages, and pass `format_with_citations(results)` into their prompt
  so the model answers using only retrieved, sourced content.
- **Multilingual support**: the embedding model
  (`paraphrase-multilingual-mpnet-base-v2`) understands ~50 languages, so
  a query in Tamil or Hindi will still match English source documents
  semantically. BM25 keyword matching, however, is language-specific — if
  you expect a lot of non-English queries, consider adding a translation
  step before search, or ES's built-in language analyzers.
- **Evaluation is not one-and-done**: re-run `evaluate.py` every time you
  change chunk size, embedding weights (`BM25_WEIGHT` / `VECTOR_WEIGHT` in
  `config.py`), or add new documents. Track the scores over time — that
  history is good evidence for your evaluation chapter in the report.

## Next steps to make this real (not just a demo)

1. **Replace `data/sample_documents.json` with a real corpus.** Same
   schema (`id`, `title`, `jurisdiction`, `doc_type`, `source_authority`,
   `date`, `url`, `text`). Sources to collect from:
   - India: Patents Act 1970 + Rules, AYUSH Ministry notifications, TKDL
     documentation, Drugs and Cosmetics Act Schedule T
   - International: WIPO IGC session documents, PCT applicant guide
   - EU: THMPD text and EMA herbal monographs
   - US: FDA botanical drug guidance documents
2. **Expand `eval/test_questions.json`** as the corpus grows — aim for
   at least 20-30 questions covering each jurisdiction before your
   final evaluation report, ideally written/reviewed by whoever on your
   team understands the legal content best.
3. **Add a "faithfulness" metric** once the LLM/generation side exists:
   for each generated answer, check whether every claim is actually
   supported by the retrieved passages (not hallucinated). This usually
   needs either manual review of a sample, or an LLM-as-judge scoring
   step — worth discussing with your team once generation is ready.
4. **Tune retrieval** by adjusting `BM25_WEIGHT` / `VECTOR_WEIGHT` in
   `config.py` and re-running `evaluate.py` to see which setting scores
   best on your test set.
