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
