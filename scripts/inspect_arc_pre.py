"""
Qualitative inspection of ARC-Easy examples from lm-eval-harness per-sample logs (samples_*.jsonl).

Purpose:
- Print a small set of ARC examples (optionally filtered) for manual inspection.

Filters:
- min/max per-sample acc
- only_incorrect: keep only items where pred_idx != correct_idx

Notes:
- This script is sample-driven, so it can be used on baseline or post-QLoRA logs
  as long as the JSONL schema matches lm-eval-harness samples_* outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualitative inspection of ARC-Easy from lm-eval samples_*.jsonl"
    )
    parser.add_argument(
        "--samples",
        type=Path,
        required=True,
        help="Path to samples_arc_easy_*.jsonl",
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
    parser.add_argument(
        "--only_incorrect",
        action="store_true",
        help="If set, only show examples where the model is wrong",
    )
    return parser.parse_args()


def get_correct_and_pred_idx(sample: dict) -> tuple[Optional[int], Optional[int]]:
    # Ground-truth index is resolved from doc.answerKey against doc.choices.label.
    doc = sample.get("doc", {})
    choices_label = doc.get("choices", {}).get("label", [])
    answer_key = doc.get("answerKey", "")

    correct_idx: Optional[int] = None
    for i, lbl in enumerate(choices_label):
        if lbl == answer_key:
            correct_idx = i
            break

    # Predicted index is computed from filtered_resps loglikelihood scores.
    filtered_resps = sample.get("filtered_resps", [])
    if not filtered_resps:
        pred_idx: Optional[int] = None
    else:
        scores = [float(r[0]) for r in filtered_resps]
        pred_idx = max(range(len(scores)), key=lambda j: scores[j])

    return correct_idx, pred_idx


def select_examples(
    path: Path,
    limit: int,
    min_acc: Optional[float],
    max_acc: Optional[float],
    only_incorrect: bool,
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

            correct_idx, pred_idx = get_correct_and_pred_idx(obj)

            if only_incorrect:
                # Keep only cases where we can compare indices and the prediction is wrong.
                if correct_idx is None or pred_idx is None:
                    continue
                if pred_idx == correct_idx:
                    continue

            examples.append(obj)
            if len(examples) >= limit:
                break

    return examples


def pretty_print_example(sample: dict) -> None:
    doc = sample["doc"]
    question = doc.get("question", "")
    choices_text = doc.get("choices", {}).get("text", [])
    choices_label = doc.get("choices", {}).get("label", [])
    answer_key = doc.get("answerKey", "")
    acc_val = float(sample.get("acc", 0.0))
    acc_norm_val = float(sample.get("acc_norm", 0.0))
    doc_id = sample.get("doc_id", None)

    correct_idx, pred_idx = get_correct_and_pred_idx(sample)

    print("=" * 80)
    print(f"doc_id: {doc_id}")
    print(f"acc: {acc_val:.6f}  |  acc_norm: {acc_norm_val:.6f}")
    print()
    print("Question:")
    print(question)
    print()
    print("Choices:")
    for i, (lbl, txt) in enumerate(zip(choices_label, choices_text)):
        marks = []
        if correct_idx is not None and i == correct_idx:
            marks.append("GT")
        if pred_idx is not None and i == pred_idx:
            marks.append("PRED")
        tag = ""
        if marks:
            tag = "  [" + ",".join(marks) + "]"
        print(f"  [{lbl}] {txt}{tag}")

    print()
    print(f"Correct index: {correct_idx}  (label={answer_key})")
    print(f"Predicted index: {pred_idx}")
    print()


def main() -> None:
    args = parse_args()
    examples = select_examples(
        path=args.samples,
        limit=args.limit,
        min_acc=args.min_acc,
        max_acc=args.max_acc,
        only_incorrect=args.only_incorrect,
    )

    if not examples:
        print("No examples matched the selected filters.")
        return

    for sample in examples:
        pretty_print_example(sample)


if __name__ == "__main__":
    main()
