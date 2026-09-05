"""
translator.py
-------------
IndicTrans2-based translation for IP-SAKTI Sahayak.

Wraps AI4Bharat's IndicTrans2 models (via HuggingFace transformers +
IndicTransToolkit) to translate between English and 22 scheduled
Indian languages, in both directions:

    Indic -> English   (user query normalization, for retrieval/QA)
    English -> Indic   (localizing the generated answer back to the
                        user's language)

Uses the distilled 200M-parameter checkpoints by default (fast enough
for interactive use on CPU/small GPU); pass `size="1B"` for the larger,
more accurate checkpoints if you have the GPU budget.

Reference: https://github.com/AI4Bharat/IndicTrans2
"""

from functools import lru_cache
from typing import List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

try:
    from IndicTransToolkit.processor import IndicProcessor
except ImportError as e:
    raise ImportError(
        "IndicTransToolkit is required. Install with: pip install IndicTransToolkit"
    ) from e

_MODEL_NAMES = {
    ("indic", "en", "200M"): "ai4bharat/indictrans2-indic-en-dist-200M",
    ("en", "indic", "200M"): "ai4bharat/indictrans2-en-indic-dist-200M",
    ("indic", "indic", "200M"): "ai4bharat/indictrans2-indic-indic-dist-320M",
    ("indic", "en", "1B"): "ai4bharat/indictrans2-indic-en-1B",
    ("en", "indic", "1B"): "ai4bharat/indictrans2-en-indic-1B",
    ("indic", "indic", "1B"): "ai4bharat/indictrans2-indic-indic-1B",
}

_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _direction_of(src_lang: str, tgt_lang: str) -> str:
    """Pick the right IndicTrans2 checkpoint family for a given
    src/tgt FLORES code pair."""
    if src_lang == "eng_Latn" and tgt_lang != "eng_Latn":
        return "en"      # en -> indic checkpoint
    if src_lang != "eng_Latn" and tgt_lang == "eng_Latn":
        return "indic"   # indic -> en checkpoint
    if src_lang != "eng_Latn" and tgt_lang != "eng_Latn":
        return "indic-indic"
    raise ValueError("src_lang and tgt_lang cannot both be eng_Latn")


class IndicTrans2Translator:
    """Loads and serves IndicTrans2 models lazily (only the checkpoint(s)
    actually needed get downloaded/loaded into memory)."""

    def __init__(self, size: str = "200M", device: str = _DEVICE):
        self.size = size
        self.device = device
        self._models = {}
        self._tokenizers = {}
        self._ip = IndicProcessor(inference=True)

    def _load(self, family: str):
        """family: 'indic' (indic->en), 'en' (en->indic), or 'indic-indic'."""
        if family in self._models:
            return self._models[family], self._tokenizers[family]

        if family == "indic":
            model_name = _MODEL_NAMES[("indic", "en", self.size)]
        elif family == "en":
            model_name = _MODEL_NAMES[("en", "indic", self.size)]
        else:
            model_name = _MODEL_NAMES[("indic", "indic", self.size)]

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, trust_remote_code=True
        ).to(self.device)
        model.eval()

        self._models[family] = model
        self._tokenizers[family] = tokenizer
        return model, tokenizer

    @torch.no_grad()
    def translate(self, sentences: List[str] | str, src_lang: str, tgt_lang: str) -> List[str]:
        """
        Translate a sentence or list of sentences from `src_lang` to
        `tgt_lang`. Both are FLORES-200 codes, e.g. "hin_Deva", "eng_Latn".
        """
        if src_lang == tgt_lang:
            return [sentences] if isinstance(sentences, str) else list(sentences)

        single_input = isinstance(sentences, str)
        batch_in = [sentences] if single_input else list(sentences)

        family = _direction_of(src_lang, tgt_lang)
        model, tokenizer = self._load(family)

        preprocessed = self._ip.preprocess_batch(
            batch_in, src_lang=src_lang, tgt_lang=tgt_lang
        )
        inputs = tokenizer(
            preprocessed, truncation=True, padding="longest", return_tensors="pt"
        ).to(self.device)

        generated = model.generate(
            **inputs,
            use_cache=True,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
        )

        with tokenizer.as_target_tokenizer():
            decoded = tokenizer.batch_decode(
                generated.detach().cpu().tolist(),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

        results = self._ip.postprocess_batch(decoded, lang=tgt_lang)
        return results[0] if single_input else results

    def to_english(self, sentences: List[str] | str, src_lang: str) -> List[str] | str:
        return self.translate(sentences, src_lang=src_lang, tgt_lang="eng_Latn")

    def from_english(self, sentences: List[str] | str, tgt_lang: str) -> List[str] | str:
        return self.translate(sentences, src_lang="eng_Latn", tgt_lang=tgt_lang)


@lru_cache(maxsize=1)
def get_default_translator() -> IndicTrans2Translator:
    """Process-wide singleton so the FastAPI backend doesn't reload
    models on every request."""
    return IndicTrans2Translator(size="200M")


if __name__ == "__main__":
    t = get_default_translator()
    hi = "आयुर्वेदिक औषधियों के लिए पेटेंट पंजीकरण प्रक्रिया क्या है?"
    en = t.to_english(hi, src_lang="hin_Deva")
    print("Hindi  ->", hi)
    print("English->", en)
    back = t.from_english(en, tgt_lang="hin_Deva")
    print("Back   ->", back)
