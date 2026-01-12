"""
Qualitative inspection of TruthfulQA_mc2 examples from lm-eval-harness per-sample logs (samples_*.jsonl).

Purpose:
- Print a small set of TruthfulQA items filtered by the per-item MC2 score `acc`.

Notes:
- `acc` here is the probability mass assigned to options labeled as true (continuous).
- Predicted index is computed from filtered_resps loglikelihood scores (argmax).
- This script is identical to inspect_truthfulqa_pre.py; only the intended use differs (post-QLoRA logs).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualitative inspection of TruthfulQA_mc2 from lm-eval samples_*.jsonl (post-QLoRA)"
    )
    parser.add_argument(
        "--samples",
        type=Path,
        required=True,
        help="Path to samples_truthfulqa_mc2_*.jsonl",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of examples to display",
    )
    parser.add_argument(
        "--min_acc",
        type=float,
        default=None,
        help="Filter by minimum per-sample acc (inclusive)",
    )
    parser.add_argument(
        "--max_acc",
        type=float,
        default=None,
        help="Filter by maximum per-sample acc (inclusive)",
    )
    return parser.parse_args()


def select_examples(
    path: Path,
    limit: int,
    min_acc: Optional[float],
    max_acc: Optional[float],
) -> List[dict]:
    examples: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            acc_val = float(obj.get("acc", 0.0))

            if min_acc is not None and acc_val < min_acc:
                continue
            if max_acc is not None and acc_val > max_acc:
                continue

            examples.append(obj)
            if len(examples) >= limit:
                break
    return examples


def get_prediction_info(sample: dict) -> Tuple[int, float]:
    # filtered_resps is a list of [loglik, ...] per option.
    scores = [float(r[0]) for r in sample.get("filtered_resps", [])]
    if not scores:
        return -1, 0.0
    best_idx = max(range(len(scores)), key=lambda i: scores[i])
    return best_idx, scores[best_idx]


def pretty_print_example(sample: dict) -> None:
    doc = sample["doc"]
    question = doc.get("question", "")
    choices = doc.get("mc2_targets", {}).get("choices", [])
    labels = doc.get("mc2_targets", {}).get("labels", [])
    acc_val = float(sample.get("acc", 0.0))
    doc_id = sample.get("doc_id", None)

    pred_idx, pred_score = get_prediction_info(sample)

    print("=" * 80)
    print(f"doc_id: {doc_id}")
    print(f"acc (probability mass on true answers): {acc_val:.6f}")
    print()
    print("Question:")
    print(question)
    print()
    print("Choices (mc2_targets):")
    for i, (choice, label) in enumerate(zip(choices, labels)):
        mark = "T" if label == 1 else "F"
        pred_mark = " <-- pred" if i == pred_idx else ""
        print(f"  [{i}] ({mark}) {choice}{pred_mark}")

    print()
    print(f"Predicted index (by log-likelihood): {pred_idx}")
    print(f"Predicted log-likelihood: {pred_score:.4f}")
    print()
    print("Per-sample acc is interpreted as the probability mass assigned to T options.")
    print()


def main() -> None:
    args = parse_args()
    examples = select_examples(
        path=args.samples,
        limit=args.limit,
        min_acc=args.min_acc,
        max_acc=args.max_acc,
    )

    if not examples:
        print("No examples matched the selected filters.")
        return

    for sample in examples:
        pretty_print_example(sample)


if __name__ == "__main__":
    main()
