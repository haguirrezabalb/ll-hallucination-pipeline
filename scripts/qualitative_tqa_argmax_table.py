#!/usr/bin/env python3
"""
scripts/qualitative_tqa_argmax_table.py

Purpose:
- Print a compact CSV-like table of the largest per-item TruthfulQA_mc2 acc changes (Δacc)
  between baseline and one post-QLoRA adapter, using lm-eval-harness samples_*.jsonl.

Inputs (latest by mtime):
- Baseline samples:
    evals/baseline/baseline_truthfulqa_mc2_seed{seed}/**/samples_truthfulqa_mc2_*.jsonl
- Post samples (by_adapter view):
    evals/postqlora/by_adapter/{adapter}/truthfulqa_mc2_seed{seed}/samples_truthfulqa_mc2_*.jsonl

Outputs:
- Prints two sections to stdout:
  - TOP +Δacc (improvements)
  - TOP -Δacc (degradations)
  Each row includes: delta_acc, doc_id, acc_pre, acc_post, argmax_pre, argmax_post, question

Notes:
- TruthfulQA_mc2 acc is the MC2 probability mass assigned to true options (continuous).
- The argmax shown is the max loglikelihood option (from filtered_resps) and is tagged as (T)/(F)
  based on mc2_targets.labels.

Determinism / reruns:
- File selection uses newest-by-mtime to be rerun-safe.
- Sorting is deterministic given the selected baseline/post files.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Dict


TASK = "truthfulqa_mc2"


def newest(pattern: str) -> str:
    # Select newest file by mtime to be robust to reruns (multiple samples_*.jsonl).
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise FileNotFoundError(f"No match: {pattern}")
    return max(files, key=os.path.getmtime)


def load_samples_map(path: str) -> Dict[int, dict]:
    # Load samples JSONL into a {doc_id -> sample} map for alignment.
    out: Dict[int, dict] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            out[int(obj["doc_id"])] = obj
    return out


def argmax_idx(sample: dict) -> int:
    # Compute argmax over filtered_resps loglikelihood scores.
    resps = sample.get("filtered_resps", [])
    if not resps:
        return -1
    scores = [float(r[0]) for r in resps]
    return max(range(len(scores)), key=lambda i: scores[i])


def mc2_choice_text(sample: dict, idx: int) -> str:
    doc = sample.get("doc", {})
    mc2 = doc.get("mc2_targets", {})
    choices = mc2.get("choices", [])
    if idx < 0 or idx >= len(choices):
        return "<no_choice>"
    return str(choices[idx])


def mc2_is_true(sample: dict, idx: int) -> bool:
    doc = sample.get("doc", {})
    mc2 = doc.get("mc2_targets", {})
    labels = mc2.get("labels", [])
    if idx < 0 or idx >= len(labels):
        return False
    return int(labels[idx]) == 1


def trunc(s: str, n: int) -> str:
    # Normalize whitespace and truncate to keep the table readable.
    s = " ".join(str(s).split())
    return s if len(s) <= n else (s[: n - 1] + "…")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Print a TOP-K Δacc table for TruthfulQA_mc2 (baseline vs one adapter).")
    p.add_argument("--adapter", default="dolly_full", help="Adapter id under evals/postqlora/by_adapter/")
    p.add_argument("--seed", type=int, default=0, help="Evaluation seed (default: 0)")
    p.add_argument("--topk", type=int, default=8, help="Top-K items to print for best/worst (default: 8)")
    p.add_argument("--max_chars", type=int, default=90, help="Max chars for argmax choice text (default: 90)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    seed = args.seed
    adapter = args.adapter
    topk = args.topk
    max_chars = args.max_chars

    baseline_pattern = f"evals/baseline/baseline_{TASK}_seed{seed}/**/samples_{TASK}_*.jsonl"
    post_pattern = f"evals/postqlora/by_adapter/{adapter}/{TASK}_seed{seed}/samples_{TASK}_*.jsonl"

    baseline_path = newest(baseline_pattern)
    post_path = newest(post_pattern)

    pre = load_samples_map(baseline_path)
    post = load_samples_map(post_path)

    common = sorted(set(pre.keys()) & set(post.keys()))
    rows = []

    for did in common:
        a = pre[did]
        b = post[did]

        acc_pre = float(a.get("acc", 0.0))
        acc_post = float(b.get("acc", 0.0))
        dacc = acc_post - acc_pre

        pre_idx = argmax_idx(a)
        post_idx = argmax_idx(b)

        pre_txt = trunc(mc2_choice_text(a, pre_idx), max_chars)
        post_txt = trunc(mc2_choice_text(b, post_idx), max_chars)

        pre_tf = "T" if mc2_is_true(a, pre_idx) else "F"
        post_tf = "T" if mc2_is_true(b, post_idx) else "F"

        q = a.get("doc", {}).get("question", "")
        q = trunc(q, 120)

        rows.append(
            {
                "delta_acc": dacc,
                "doc_id": did,
                "acc_pre": acc_pre,
                "acc_post": acc_post,
                "argmax_pre": f"\"{pre_txt}\" ({pre_tf})",
                "argmax_post": f"\"{post_txt}\" ({post_tf})",
                "question": q,
            }
        )

    rows_sorted = sorted(rows, key=lambda r: r["delta_acc"], reverse=True)
    best = rows_sorted[:topk]
    worst = list(reversed(rows_sorted[-topk:]))

    print(f"# Baseline: {os.path.basename(baseline_path)}")
    print(f"# Post ({adapter}): {os.path.basename(post_path)}")
    print("# Columns: delta_acc,doc_id,acc_pre,acc_post,argmax_pre,argmax_post,question")
    print()

    print("## TOP +Δacc (improvements)")
    print("delta_acc,doc_id,acc_pre,acc_post,argmax_pre,argmax_post,question")
    for r in best:
        print(
            f"{r['delta_acc']:+.6f},{r['doc_id']},{r['acc_pre']:.6f},{r['acc_post']:.6f},"
            f"{r['argmax_pre']},{r['argmax_post']},\"{r['question']}\""
        )

    print()
    print("## TOP -Δacc (degradations)")
    print("delta_acc,doc_id,acc_pre,acc_post,argmax_pre,argmax_post,question")
    for r in worst:
        print(
            f"{r['delta_acc']:+.6f},"
            f"{r['doc_id']},"
            f"{r['acc_pre']:.6f},"
            f"{r['acc_post']:.6f},"
            f"{r['argmax_pre']},"
            f"{r['argmax_post']},"
            f"\"{r['question']}\""
        )


if __name__ == "__main__":
    main()
