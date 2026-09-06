"""
pipeline.py
-----------
End-to-end Multilingual NLP pipeline for IP-SAKTI Sahayak.

This is the module the rest of the team (RAG Core / Backend APIs)
should import and call. It ties together:

    1. lang_detect.py   -> detect the user's query language
    2. translator.py    -> IndicTrans2: normalize query to English,
                            and later localize the generated answer
                            back to the user's language
    3. embeddings.py    -> Sentence-Transformers: embed the (English)
                            query for Qdrant retrieval

Typical flow in the larger system:

    query (any of 22 Indian languages, or English)
        │
        ▼
   process_query()   <-- THIS MODULE
        │  {detected_lang, english_query, query_embedding}
        ▼
   [Team 1: Qdrant similarity search using query_embedding]
        ▼
   [Team 6: Regulatory QA / answer generation, in English]
        │  english_answer
        ▼
   localize_answer()  <-- THIS MODULE
        │
        ▼
   final answer, in the user's original language, with citations
"""

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from lang_detect import detect_language, FLORES_TO_NAME
from translator import get_default_translator
from embeddings import get_default_embedder


@dataclass
class QueryResult:
    original_query: str
    detected_lang: str                 # FLORES-200 code, e.g. "hin_Deva"
    detected_lang_name: str             # human readable, e.g. "Hindi"
    english_query: str                  # query normalized to English
    query_embedding: np.ndarray          # vector for Qdrant search
    response_lang: str = field(default="")  # lang to translate the answer back into

    def __post_init__(self):
        if not self.response_lang:
            self.response_lang = self.detected_lang


class MultilingualNLPPipeline:
    def __init__(self):
        self.translator = get_default_translator()
        self.embedder = get_default_embedder()

    def process_query(self, text: str, response_lang: Optional[str] = None) -> QueryResult:
        """
        Full incoming-query pipeline: detect language, translate to
        English for retrieval, and embed for Qdrant vector search.

        `response_lang` lets the caller override which language the
        final answer should be localized into (defaults to the
        detected query language).
        """
        detected = detect_language(text)

        english_query = (
            text if detected == "eng_Latn"
            else self.translator.to_english(text, src_lang=detected)
        )

        embedding = self.embedder.embed(english_query)

        return QueryResult(
            original_query=text,
            detected_lang=detected,
            detected_lang_name=FLORES_TO_NAME.get(detected, detected),
            english_query=english_query,
            query_embedding=embedding,
            response_lang=response_lang or detected,
        )

    def localize_answer(self, english_answer: str, target_lang: str) -> str:
        """
        Translate a generated English answer back into the user's
        language. Pass target_lang="eng_Latn" (or call is skipped
        naturally) when the user's query was already in English.
        """
        if target_lang == "eng_Latn":
            return english_answer
        return self.translator.from_english(english_answer, tgt_lang=target_lang)

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """
        Convenience passthrough for the Data Engineering module (#4)
        to embed source documents with the SAME model used for
        queries, guaranteeing compatibility with Qdrant search.
        """
        return self.embedder.embed(texts)


if __name__ == "__main__":
    pipeline = MultilingualNLPPipeline()

    query = "आयुर्वेदिक औषधियों के लिए पेटेंट पंजीकरण प्रक्रिया क्या है?"
    result = pipeline.process_query(query)

    print("Original query :", result.original_query)
    print("Detected lang  :", result.detected_lang, f"({result.detected_lang_name})")
    print("English query  :", result.english_query)
    print("Embedding shape:", result.query_embedding.shape)

    # Simulate a generated answer coming back from Team 6's QA module
    fake_english_answer = (
        "Ayurvedic medicines can be protected via patents under the Patents Act, 1970, "
        "subject to novelty and non-obviousness requirements. Traditional formulations "
        "already documented in the Traditional Knowledge Digital Library (TKDL) are "
        "generally not patentable. [Source: Patents Act 1970, Section 3(p)]"
    )
    localized = pipeline.localize_answer(fake_english_answer, target_lang=result.response_lang)
    print("\nLocalized answer:\n", localized)
