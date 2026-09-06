"""
Basic unit tests for cleaning and chunking - run with: pytest tests/
No DB/model download required for these; they test pure text logic.
"""

from src.cleaner_chunker import clean_text, chunk_section


def test_clean_text_removes_page_numbers():
    raw = "Some legal clause text.   Page 3 of 10   More text here."
    cleaned = clean_text(raw)
    assert "Page 3 of 10" not in cleaned
    assert "Some legal clause text." in cleaned


def test_clean_text_collapses_whitespace():
    raw = "Text   with     irregular\n\nspacing"
    cleaned = clean_text(raw)
    assert "  " not in cleaned


def test_chunk_section_respects_max_tokens():
    long_text = " ".join([f"This is sentence number {i}." for i in range(200)])
    chunks = chunk_section(
        doc_id="test_doc",
        section_text=long_text,
        section_label="Section 5",
        page_number=1,
        max_tokens=50,
        overlap_tokens=5,
    )
    assert len(chunks) > 1
    for chunk in chunks:
        # allow small overshoot since we don't split mid-sentence
        assert chunk.token_count <= 60


def test_chunk_section_empty_text_returns_no_chunks():
    chunks = chunk_section(
        doc_id="test_doc",
        section_text="   ",
        section_label=None,
        page_number=1,
    )
    assert chunks == []


def test_chunk_section_preserves_metadata():
    chunks = chunk_section(
        doc_id="doc_123",
        section_text="Short section text for testing metadata propagation.",
        section_label="Clause 4(a)",
        page_number=7,
    )
    assert len(chunks) == 1
    assert chunks[0].doc_id == "doc_123"
    assert chunks[0].section_or_clause == "Clause 4(a)"
    assert chunks[0].page_number == 7
