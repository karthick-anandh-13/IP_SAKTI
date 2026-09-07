"""
Core RAG orchestration.

Pipeline for every query:
  1. Detect input language (so Hindi/Tamil/etc. queries get flagged correctly).
  2. Embed the query with the SAME multilingual encoder used at ingestion time.
  3. Retrieve top-k passages from Qdrant, optionally filtered by jurisdiction /
     doc type, above a minimum similarity threshold.
  4. Synthesize an answer STRICTLY from retrieved passages -- the prompt
     forbids adding facts not present in context, and every sentence in the
     answer must map to at least one citation.
  5. Return the answer plus a structured citation list (clickable via
     official_url) so the caller can render "traceable" links.

Two synthesis backends are supported:
  - "anthropic": calls Claude for fluent, grounded synthesis.
  - "template": pure extractive fallback with zero external API calls, so the
    prototype is fully runnable offline / during grading without a key.
"""
from langdetect import DetectorFactory, detect

from app.config import get_settings
from app.embeddings import get_embedder
from app.schemas import Citation, DocType, Jurisdiction, QueryRequest, QueryResponse
from app.vectorstore import build_filter, search

DetectorFactory.seed = 0  # deterministic langdetect

_LANG_NAME = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "sa": "Sanskrit",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
    "mr": "Marathi",
}

_NO_RESULTS_MSG = {
    "en": "I could not find any verified source in the knowledge base that "
    "addresses this query with sufficient confidence. Please rephrase, or "
    "consult the relevant statutory authority directly.",
    "hi": "मुझे इस प्रश्न के लिए ज्ञान आधार में पर्याप्त विश्वसनीय स्रोत नहीं मिला। "
    "कृपया प्रश्न को दोबारा लिखें या संबंधित प्राधिकरण से सीधे संपर्क करें।",
}


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


def run_query(request: QueryRequest) -> QueryResponse:
    settings = get_settings()
    detected_lang = detect_language(request.query)
    response_lang = request.response_language or (
        detected_lang if settings.default_response_language == "auto" else settings.default_response_language
    )

    embedder = get_embedder()
    query_vector = embedder.embed_query(request.query)

    qfilter = build_filter(request.jurisdiction_filter, request.doc_type_filter)
    hits = search(
        query_vector=query_vector,
        top_k=request.top_k or settings.top_k,
        score_threshold=settings.score_threshold,
        qfilter=qfilter,
    )

    if not hits:
        return QueryResponse(
            query=request.query,
            detected_language=detected_lang,
            answer=_NO_RESULTS_MSG.get(response_lang, _NO_RESULTS_MSG["en"]),
            citations=[],
        )

    citations = [_hit_to_citation(h) for h in hits]
    answer = synthesize_answer(request.query, hits, response_lang)

    return QueryResponse(
        query=request.query,
        detected_language=detected_lang,
        answer=answer,
        citations=citations,
    )


def _hit_to_citation(hit) -> Citation:
    payload = hit.payload
    return Citation(
        doc_id=payload["doc_id"],
        title=payload["title"],
        doc_type=DocType(payload["doc_type"]),
        jurisdiction=Jurisdiction(payload["jurisdiction"]),
        clause_or_section=payload.get("clause_or_section"),
        official_url=payload.get("official_url"),
        relevance_score=round(float(hit.score), 4),
        snippet=payload["text"][:280].strip() + ("..." if len(payload["text"]) > 280 else ""),
    )


# --------------------------------------------------------------------------
# Answer synthesis backends
# --------------------------------------------------------------------------

def synthesize_answer(query: str, hits: list, response_lang: str) -> str:
    settings = get_settings()
    if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        return _synthesize_with_anthropic(query, hits, response_lang)
    return _synthesize_extractive(query, hits, response_lang)


_SYSTEM_PROMPT = """You are IP-SAKTI Sahayak, an assistant for Intellectual Property \
and regulatory guidance in Ayurveda. Answer ONLY using the numbered CONTEXT \
passages below -- never introduce facts, dates, section numbers, or claims \
that are not present in the context. If the context is insufficient, say so \
explicitly rather than guessing.

After every sentence or claim, cite the source using its bracketed number, \
e.g. [1], [2]. Multiple sources may support one sentence, e.g. [1][3]. \
Respond in the same language as the user's query where possible. Keep the \
answer precise, structured, and suitable for a legal/regulatory context."""


def _build_context_block(hits: list) -> str:
    lines = []
    for i, h in enumerate(hits, start=1):
        p = h.payload
        header = f"[{i}] {p['title']}"
        if p.get("clause_or_section"):
            header += f", {p['clause_or_section']}"
        header += f" ({p['jurisdiction']}, {p['doc_type']})"
        lines.append(f"{header}\n{p['text']}")
    return "\n\n".join(lines)


def _synthesize_with_anthropic(query: str, hits: list, response_lang: str) -> str:
    import anthropic

    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    context_block = _build_context_block(hits)

    lang_hint = _LANG_NAME.get(response_lang, response_lang)
    user_msg = (
        f"CONTEXT:\n{context_block}\n\n"
        f"USER QUERY ({lang_hint}): {query}\n\n"
        "Write the grounded, cited answer now."
    )

    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=800,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def _synthesize_extractive(query: str, hits: list, response_lang: str) -> str:
    """
    No-API-key fallback: assembles a structured, cited answer directly from
    the retrieved passages. Deterministic and fully offline -- useful for
    demoing the retrieval + citation pipeline without any LLM cost.
    """
    lines = [f"Based on {len(hits)} verified source(s) relevant to your query:\n"]
    for i, h in enumerate(hits, start=1):
        p = h.payload
        ref = p["title"]
        if p.get("clause_or_section"):
            ref += f" — {p['clause_or_section']}"
        snippet = p["text"].strip()
        if len(snippet) > 400:
            snippet = snippet[:400].rsplit(" ", 1)[0] + "..."
        lines.append(f"{i}. {ref} [{i}]\n   {snippet}")
    lines.append(
        "\nReview each numbered citation below for the full clause text and "
        "official link before relying on this guidance."
    )
    return "\n".join(lines)
