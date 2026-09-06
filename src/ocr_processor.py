"""
OCR module.
Used only for scanned PDFs (gazette notifications, old patent scans)
where PyMuPDF cannot extract a text layer directly.
"""

import logging
from typing import Tuple

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

from config.settings import TESSERACT_CMD, OCR_LANGUAGES, OCR_CONFIDENCE_THRESHOLD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

logger = logging.getLogger(__name__)


def page_has_text_layer(page: fitz.Page, min_chars: int = 20) -> bool:
    """Quick check: does this PDF page already have extractable text,
    or is it a scanned image that needs OCR?"""
    text = page.get_text().strip()
    return len(text) >= min_chars


def ocr_page(page: fitz.Page, dpi: int = 300) -> Tuple[str, float]:
    """
    Render a PDF page to an image and run OCR on it.
    Returns (extracted_text, average_confidence_percentage).
    """
    pix = page.get_pixmap(dpi=dpi)
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))

    ocr_data = pytesseract.image_to_data(
        image, lang=OCR_LANGUAGES, output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []
    for i, word in enumerate(ocr_data["text"]):
        conf = int(ocr_data["conf"][i]) if ocr_data["conf"][i] != "-1" else -1
        if word.strip() and conf >= 0:
            words.append(word)
            confidences.append(conf)

    text = " ".join(words)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    if avg_confidence < OCR_CONFIDENCE_THRESHOLD:
        logger.warning(
            "Low OCR confidence (%.1f%%) - page flagged for manual review", avg_confidence
        )

    return text, avg_confidence


def process_pdf_with_ocr_fallback(file_path: str) -> list[dict]:
    """
    Walks every page of a PDF. Uses native text extraction where possible,
    falls back to OCR for scanned/image-only pages.

    Returns a list of dicts: [{page_number, text, ocr_used, ocr_confidence}, ...]
    """
    doc = fitz.open(file_path)
    results = []

    for page_num, page in enumerate(doc, start=1):
        if page_has_text_layer(page):
            results.append({
                "page_number": page_num,
                "text": page.get_text(),
                "ocr_used": False,
                "ocr_confidence": None,
            })
        else:
            text, confidence = ocr_page(page)
            results.append({
                "page_number": page_num,
                "text": text,
                "ocr_used": True,
                "ocr_confidence": confidence,
            })

    doc.close()
    return results
