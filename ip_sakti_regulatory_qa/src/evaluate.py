 """
Evaluation framework for IP-SAKTI Sahayak — Regulatory Intelligence & QA.

This is the core of the "QA" part of your role. It answers the question:
"How good is our retrieval, and is it citing the right sources?"

Metrics computed per query, then averaged across the whole test set:
  - Precision@k   : of the top-k retrieved chunks, what fraction came from
                    a document we expected to be relevant?
  - Recall@k      : of the documents we expected, what fraction were
                    retrieved somewhere in the top-k?
  - MRR           : Mean Reciprocal Rank — rewards getting a correct
                    document near the TOP of the results, not just present.
  - Keyword hit rate : sanity check that expected legal/regulatory terms
                    actually appear in the retrieved text (a proxy for
                    whether the LLM will have the right facts to cite).

Run:
    python src/evaluate.py
    python src/evaluate.py --top_k 3
    python src/evaluate.py --output eval/results.csv
"""

import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import config
from search import hybrid_search


def precision_at_k(retrieved_doc_ids, expected_doc_ids):
    if not retrieved_doc_ids:
        return 0.0
    hits = sum(1 for d in retrieved_doc_ids if d in expected_doc_ids)
    return hits / len(retrieved_doc_ids)


def recall_at_k(retrieved_doc_ids, expected_doc_ids):
    if not expected_doc_ids:
        return None
    hits = sum(1 for d in expected_doc_ids if d in retrieved_doc_ids)
    return hits / len(expected_doc_ids)


def reciprocal_rank(retrieved_doc_ids, expected_doc_ids):
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in expected_doc_ids:
            return 1.0 / rank
    return 0.0


def keyword_hit_rate(retrieved_texts, expected_keywords):
    if not expected_keywords:
        return None
    combined_text = " ".join(retrieved_texts).lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in combined_text)
    return hits / len(expected_keywords)


def load_test_set(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate(test_set, top_k: int):
    rows = []
    for item in test_set:
        results = hybrid_search(item["question"], top_k=top_k)
        retrieved_doc_ids = [r["doc_id"] for r in results]
        retrieved_texts = [r["text"] for r in results]

        row = {
            "question": item["question"],
            "expected_doc_ids": ", ".join(item["expected_doc_ids"]),
            "retrieved_doc_ids": ", ".join(retrieved_doc_ids),
            "precision_at_k": precision_at_k(retrieved_doc_ids, item["expected_doc_ids"]),
            "recall_at_k": recall_at_k(retrieved_doc_ids, item["expected_doc_ids"]),
            "reciprocal_rank": reciprocal_rank(retrieved_doc_ids, item["expected_doc_ids"]),
            "keyword_hit_rate": keyword_hit_rate(retrieved_texts, item.get("expected_keywords", [])),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def print_summary(df: pd.DataFrame, top_k: int):
    print(f"\n=== Retrieval Evaluation Summary (top_k={top_k}) ===")
    print(f"Questions evaluated : {len(df)}")
    print(f"Mean Precision@{top_k}  : {df['precision_at_k'].mean():.3f}")
    print(f"Mean Recall@{top_k}     : {df['recall_at_k'].mean():.3f}")
    print(f"Mean Reciprocal Rank : {df['reciprocal_rank'].mean():.3f}")
    print(f"Mean Keyword Hit Rate: {df['keyword_hit_rate'].mean():.3f}")
    print()
    print("Per-question breakdown:")
    with pd.option_context("display.max_colwidth", 60):
        print(df[["question", "precision_at_k", "recall_at_k", "reciprocal_rank"]].to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Evaluate the regulatory retrieval pipeline.")
    parser.add_argument("--top_k", type=int, default=config.TOP_K, help="Number of chunks to retrieve per query.")
    parser.add_argument("--output", type=str, default=None, help="Optional path to save full results as CSV.")
    args = parser.parse_args()

    eval_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "eval", "test_questions.json",
    )
    test_set = load_test_set(eval_path)

    df = evaluate(test_set, args.top_k)
    print_summary(df, args.top_k)

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
