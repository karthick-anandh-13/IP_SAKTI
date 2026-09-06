"""
Main ingestion pipeline.
Ties together: extraction -> chunking -> embedding -> storage.

Usage:
    python -m src.pipeline --file data/raw/ayush_gazette_2023.pdf \
        --jurisdiction India-AYUSH --source-type gazette \
        --title "AYUSH Notification 2023" --doc-id ayush_2023_001
"""

import argparse
import logging
import uuid

from src.pdf_extractor import extract_document
from src.cleaner_chunker import chunk_document
from src.embedder import embed_chunks
from src.schema import DocumentMetadata
from src.db import init_db, save_document_metadata, save_chunks

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(
    file_path: str,
    jurisdiction: str,
    source_type: str,
    title: str,
    doc_id: str = None,
    source_url: str = None,
    act_or_regulation_name: str = None,
):
    doc_id = doc_id or str(uuid.uuid4())

    logger.info("STEP 1/4: Extracting text from %s", file_path)
    pages = extract_document(file_path)

    # Flag whether OCR was used anywhere and capture the lowest confidence seen,
    # so low-quality documents can be routed for manual review.
    ocr_used = any(p["ocr_used"] for p in pages)
    ocr_confidences = [p["ocr_confidence"] for p in pages if p["ocr_confidence"] is not None]
    min_confidence = min(ocr_confidences) if ocr_confidences else None

    metadata = DocumentMetadata(
        doc_id=doc_id,
        title=title,
        jurisdiction=jurisdiction,
        source_type=source_type,
        source_url=source_url,
        act_or_regulation_name=act_or_regulation_name,
        file_path=file_path,
        ocr_used=ocr_used,
        ocr_confidence=min_confidence,
    )

    logger.info("STEP 2/4: Chunking document (clause-aware)")
    chunks = chunk_document(doc_id, pages)

    logger.info("STEP 3/4: Generating multilingual embeddings")
    embedded_chunks = embed_chunks(chunks)

    logger.info("STEP 4/4: Saving to database")
    save_document_metadata(metadata)
    save_chunks(embedded_chunks)

    logger.info(
        "DONE. doc_id=%s | pages=%d | chunks=%d | ocr_used=%s",
        doc_id, len(pages), len(chunks), ocr_used,
    )
    return doc_id, len(chunks)


def main():
    parser = argparse.ArgumentParser(description="IP-SAKTI Sahayak ingestion pipeline")
    parser.add_argument("--file", required=True, help="Path to the source PDF")
    parser.add_argument("--jurisdiction", required=True)
    parser.add_argument("--source-type", required=True,
                         choices=["gazette", "patent", "statute", "guideline", "classical_text"])
    parser.add_argument("--title", required=True)
    parser.add_argument("--doc-id", default=None)
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--act-name", default=None)

    args = parser.parse_args()

    init_db()
    run_pipeline(
        file_path=args.file,
        jurisdiction=args.jurisdiction,
        source_type=args.source_type,
        title=args.title,
        doc_id=args.doc_id,
        source_url=args.source_url,
        act_or_regulation_name=args.act_name,
    )


if __name__ == "__main__":
    main()
