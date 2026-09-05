"""
lang_detect.py
--------------
Lightweight language identification for IP-SAKTI Sahayak.

Detects the language of an incoming user query and maps it to the
FLORES-200 language codes used by IndicTrans2 (e.g. "hin_Deva",
"tam_Taml", "eng_Latn"). Detection is primarily script/Unicode-range
based, which is fast, has zero model-download cost, and is reliable
for distinguishing between languages written in different scripts.

LIMITATION: Several Indian languages share a script (e.g. Hindi,
Marathi and Sanskrit are all written in Devanagari; Bengali and
Assamese both use the Bengali script). For those cases we fall back
to a small keyword/stopword heuristic, and default to the most common
language for that script. For production-grade accuracy on these
same-script cases, swap this module out for AI4Bharat's dedicated
IndicLID model (https://github.com/AI4Bharat/IndicLID) - the rest of
the pipeline (translator.py, embeddings.py) does not need to change,
since they only depend on the FLORES-200 code this module returns.
"""

import re

# Unicode block ranges for Indian scripts
_SCRIPT_RANGES = {
    "Devanagari": (0x0900, 0x097F),   # Hindi, Marathi, Sanskrit, Nepali, Konkani
    "Bengali":    (0x0980, 0x09FF),   # Bengali, Assamese
    "Gurmukhi":   (0x0A00, 0x0A7F),   # Punjabi
    "Gujarati":   (0x0A80, 0x0AFF),   # Gujarati
    "Oriya":      (0x0B00, 0x0B7F),   # Odia
    "Tamil":      (0x0B80, 0x0BFF),   # Tamil
    "Telugu":     (0x0C00, 0x0C7F),   # Telugu
    "Kannada":    (0x0C80, 0x0CFF),   # Kannada
    "Malayalam":  (0x0D00, 0x0D7F),   # Malayalam
    "Arabic":     (0x0600, 0x06FF),   # Urdu (Arabic script)
}

# Default FLORES-200 code per script (used when script is unambiguous,
# or as the fallback default for ambiguous multi-language scripts)
_SCRIPT_TO_DEFAULT_LANG = {
    "Devanagari": "hin_Deva",
    "Bengali":    "ben_Beng",
    "Gurmukhi":   "pan_Guru",
    "Gujarati":   "guj_Gujr",
    "Oriya":      "ory_Orya",
    "Tamil":      "tam_Taml",
    "Telugu":     "tel_Telu",
    "Kannada":    "kan_Knda",
    "Malayalam":  "mal_Mlym",
    "Arabic":     "urd_Arab",
}

# Small marker-word lists to disambiguate same-script languages.
# Not exhaustive - just enough to bias common Ayurveda/regulatory queries.
_MARATHI_MARKERS = {"आहे", "आणि", "मला", "काय", "नाही", "करण्यात", "यासाठी"}
_SANSKRIT_MARKERS = {"अस्ति", "तत्", "एतत्", "स्वाहा", "पातञ्जल", "आयुर्वेद:"}
_ASSAMESE_MARKERS = {"আৰু", "নাই", "কৰা", "বাবে", "কি"}

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def _script_of(text: str) -> str | None:
    """Return the dominant Unicode script block found in `text`, or None
    if the text looks like plain ASCII/Latin (i.e. likely English)."""
    counts = {name: 0 for name in _SCRIPT_RANGES}
    for ch in text:
        cp = ord(ch)
        for name, (lo, hi) in _SCRIPT_RANGES.items():
            if lo <= cp <= hi:
                counts[name] += 1
                break
    dominant = max(counts, key=counts.get)
    return dominant if counts[dominant] > 0 else None


def detect_language(text: str) -> str:
    """
    Detect the language of `text` and return a FLORES-200 code
    compatible with IndicTrans2 (e.g. "hin_Deva", "eng_Latn").

    Falls back to "eng_Latn" for empty input or text with no
    recognizable Indic script (assumed English / romanized query).
    """
    if not text or not text.strip():
        return "eng_Latn"

    script = _script_of(text)
    if script is None:
        # No Indic script characters found -> treat as English.
        # (Romanized Hindi/Tamil etc. is a harder problem; if this
        # matters for your demo, plug in IndicLID here instead.)
        return "eng_Latn"

    if script == "Devanagari":
        words = set(text.split())
        if words & _SANSKRIT_MARKERS:
            return "san_Deva"
        if words & _MARATHI_MARKERS:
            return "mar_Deva"
        return "hin_Deva"  # default for Devanagari

    if script == "Bengali":
        words = set(text.split())
        if words & _ASSAMESE_MARKERS:
            return "asm_Beng"
        return "ben_Beng"  # default for Bengali script

    return _SCRIPT_TO_DEFAULT_LANG[script]


# Human-readable names, useful for UI display / logging
FLORES_TO_NAME = {
    "eng_Latn": "English",
    "hin_Deva": "Hindi",
    "mar_Deva": "Marathi",
    "san_Deva": "Sanskrit",
    "ben_Beng": "Bengali",
    "asm_Beng": "Assamese",
    "pan_Guru": "Punjabi",
    "guj_Gujr": "Gujarati",
    "ory_Orya": "Odia",
    "tam_Taml": "Tamil",
    "tel_Telu": "Telugu",
    "kan_Knda": "Kannada",
    "mal_Mlym": "Malayalam",
    "urd_Arab": "Urdu",
}


if __name__ == "__main__":
    samples = [
        "What is the GI tag registration process for Ayurvedic medicines?",
        "आयुर्वेदिक औषधियों के लिए पेटेंट पंजीकरण प्रक्रिया क्या है?",
        "ஆயுர்வேத மருந்துகளுக்கான காப்புரிமை பதிவு செயல்முறை என்ன?",
        "ఆయుర్వేద ఔషధాల కోసం పేటెంట్ నమోదు ప్రక్రియ ఏమిటి?",
    ]
    for s in samples:
        code = detect_language(s)
        print(f"{code:10s} ({FLORES_TO_NAME.get(code, '?'):8s}) <- {s}")
