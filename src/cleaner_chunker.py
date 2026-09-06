"""
Cleaning + chunking module.
Legal text needs clause-aware chunking - we avoid cutting a chunk in the
middle of a clause, since retrieval accuracy and citation correctness
both depend on chunk boundaries lining up with legal structure.
"""

import re
import uuid
import logging
from typing import List

from langdetect import detect, LangDetectException

from config.settings import MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS
from src.schema import TextChunk

logger = logging.getLogger(__name__)


def clean_text(raw_text: str) -> str:
    """Removes OCR noise, extra whitespace, page-number artifacts, etc."""
    text = re.sub(r"\s+", " ", raw_text)
    text = re.sub(r"Page\s*\d+\s*of\s*\d+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"-{2,}", "", text)  # OCR often produces stray dashes
    return text.strip()


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def _word_count(text: str) -> int:
    return len(text.split())


def chunk_section(
    doc_id: str,
    section_text: str,
    section_label: str | None,
    page_number: int | None,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> List[TextChunk]:
    """
    Splits a single section's text into overlapping chunks, respecting
    sentence boundaries so a chunk never ends mid-sentence.
    """
    cleaned = clean_text(section_text)
    if not cleaned:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: List[TextChunk] = []
    current_words: List[str] = []

    for sentence in sentences:
        sentence_words = sentence.split()
        if _word_count(" ".join(current_words)) + len(sentence_words) > max_tokens and current_words:
            chunk_text = " ".join(current_words)
            chunks.append(_build_chunk(doc_id, chunk_text, section_label, page_number))
            # keep overlap for context continuity
            overlap_words = current_words[-overlap_tokens:] if overlap_tokens else []
            current_words = overlap_words + sentence_words
        else:
            current_words.extend(sentence_words)

    if current_words:
        chunk_text = " ".join(current_words)
        chunks.append(_build_chunk(doc_id, chunk_text, section_label, page_number))

    return chunks


def _build_chunk(doc_id: str, text: str, section_label: str | None, page_number: int | None) -> TextChunk:
    return TextChunk(
        chunk_id=str(uuid.uuid4()),
        doc_id=doc_id,
        page_number=page_number,
        section_or_clause=section_label,
        text=text,
        token_count=_word_count(text),
        language=detect_language(text),
    )


def chunk_document(doc_id: str, pages: List[dict]) -> List[TextChunk]:
    """
    Runs chunk_section across every section of every page in the document.
    `pages` is the output of pdf_extractor.extract_document().
    """
    all_chunks: List[TextChunk] = []
    for page in pages:
        for section in page.get("sections", []):
            chunks = chunk_section(
                doc_id=doc_id,
                section_text=section["text"],
                section_label=section["label"],
                page_number=page["page_number"],
            )
            all_chunks.extend(chunks)

    logger.info("Document %s -> %d chunks", doc_id, len(all_chunks))
    return all_chunks
