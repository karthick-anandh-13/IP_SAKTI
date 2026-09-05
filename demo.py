"""
demo.py
-------
Quick demo of the full Multilingual NLP pipeline for IP-SAKTI Sahayak.

Run with:
    python demo.py

First run will download IndicTrans2 (~200M-param dist checkpoints)
and the LaBSE embedding model from HuggingFace - this needs internet
access and a few GB of disk the first time.
"""

from pipeline import MultilingualNLPPipeline

SAMPLE_QUERIES = [
    "What is the patent registration process for Ayurvedic medicines?",
    "आयुर्वेदिक औषधियों के लिए पेटेंट पंजीकरण प्रक्रिया क्या है?",   # Hindi
    "ஆயுர்வேத மருந்துகளுக்கான காப்புரிமை பதிவு செயல்முறை என்ன?",   # Tamil
    "ఆయుర్వేద ఔషధాల కోసం పేటెంట్ నమోదు ప్రక్రియ ఏమిటి?",           # Telugu
]

FAKE_ENGLISH_ANSWER = (
    "Ayurvedic formulations can be patented under the Patents Act, 1970, "
    "if they meet novelty, inventive step, and industrial applicability "
    "requirements. Formulations already recorded in the Traditional "
    "Knowledge Digital Library (TKDL) generally cannot be patented, since "
    "prior public disclosure defeats novelty."
)


def main():
    pipeline = MultilingualNLPPipeline()

    for query in SAMPLE_QUERIES:
        print("=" * 80)
        result = pipeline.process_query(query)

        print(f"Query language : {result.detected_lang_name} ({result.detected_lang})")
        print(f"Original       : {result.original_query}")
        print(f"English query  : {result.english_query}")
        print(f"Embedding shape: {result.query_embedding.shape}")
        print(f"Embedding[:5]  : {result.query_embedding[:5]}")

        # --- here Team 1 would run Qdrant similarity search using
        #     result.query_embedding, and Team 6 would generate an
        #     English answer from the retrieved chunks. We simulate
        #     that answer with FAKE_ENGLISH_ANSWER for this demo.

        localized_answer = pipeline.localize_answer(
            FAKE_ENGLISH_ANSWER, target_lang=result.response_lang
        )
        print(f"\nLocalized answer ({result.detected_lang_name}):\n{localized_answer}")

    print("=" * 80)


if __name__ == "__main__":
    main()
