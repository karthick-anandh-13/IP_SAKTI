"""
Structured extraction from PDFs using PyMuPDF.
Goes beyond plain text - tries to preserve section/clause boundaries,
since legal citation accuracy depends on knowing exactly which clause
a piece of text came from.
"""

import re
import logging
from typing import List, Dict

import fitz

from src.ocr_processor import process_pdf_with_ocr_fallback

logger = logging.getLogger(__name__)

# Common legal document section markers (extend as new doc types are added)
SECTION_PATTERNS = [
    r"^(Section|Clause|Rule|Article)\s+\d+[A-Za-z]?",
    r"^\d+\.\d+(\.\d+)?\s",       # e.g. "3.2.1 "
    r"^\(\w+\)\s",                 # e.g. "(a) "
]

SECTION_REGEX = re.compile("|".join(SECTION_PATTERNS), re.MULTILINE)


def extract_document(file_path: str) -> List[Dict]:
    """
    Extract page-wise text + best-effort section tags from a PDF,
    with automatic OCR fallback for scanned pages.

    Returns a list of page-level dicts ready for the cleaning/chunking stage.
    """
    pages = process_pdf_with_ocr_fallback(file_path)

    for page in pages:
        page["sections"] = _split_into_sections(page["text"])

    logger.info("Extracted %d pages from %s", len(pages), file_path)
    return pages


def _split_into_sections(text: str) -> List[Dict]:
    """
    Splits raw page text into (section_label, section_text) pairs based on
    detected legal section markers. Falls back to a single 'unlabeled'
    section if no markers are found - downstream chunker handles this fine.
    """
    matches = list(SECTION_REGEX.finditer(text))

    if not matches:
        return [{"label": None, "text": text.strip()}]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = text[match.start():match.end()].strip()
        section_text = text[start:end].strip()
        if section_text:
            sections.append({"label": label, "text": section_text})

    return sections


def extract_tables(file_path: str) -> List[Dict]:
    """
    Extracts tables (e.g. Schedule T classification tables, GI registers)
    using PyMuPDF's table-finding utility.
    """
    doc = fitz.open(file_path)
    all_tables = []

    for page_num, page in enumerate(doc, start=1):
        tabs = page.find_tables()
        for t_idx, tab in enumerate(tabs.tables):
            all_tables.append({
                "page_number": page_num,
                "table_index": t_idx,
                "rows": tab.extract(),
            })

    doc.close()
    return all_tables
