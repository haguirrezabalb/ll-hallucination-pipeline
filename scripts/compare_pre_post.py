#!/usr/bin/env python3
"""
scripts/compare_pre_post.py

Purpose:
- Compare baseline (pre-QLoRA) aggregated results against post-QLoRA aggregated results
  for all available adapters, and write a unified comparison CSV with deltas.

Inputs:
- Baseline (no adapters):
    evals/baseline/summary_preqlora_aggregated.csv
    columns: task,metric,mean,std,n_seeds
- Post-QLoRA (with adapters):
    evals/postqlora/summary_postqlora_aggregated.csv
    columns: adapter,task,metric,mean,std,n_seeds

Outputs:
- evals/comparison/summary_pre_post_aggregated_all_adapters.csv
  columns:
    adapter,task,metric,
    mean_pre,std_pre,n_seeds_pre,
    mean_post,std_post,n_seeds_post,
    delta

Notes:
- For standard metrics, baseline.metric == post.metric (e.g., acc, acc_norm).
- TruthfulQA uses HR_TQA naming:
    baseline: HR_TQA_pre
    post:     HR_TQA_post
  We map HR_TQA_post (post) ↔ HR_TQA_pre (baseline) and compute:
    delta = HR_TQA_post - HR_TQA_pre
  (delta < 0 means lower hallucination-rate proxy, since HR_TQA = 1 - acc(MC2)).

Determinism / reruns:
- Output rows are sorted deterministically by (adapter, task, metric).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Tuple


def load_baseline(path: Path) -> Dict[Tuple[str, str], dict]:
    # Index baseline rows for O(1) lookup by (task, metric).
    data: Dict[Tuple[str, str], dict] = {}

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = row["task"]
            metric = row["metric"]
            mean = float(row["mean"])
            std = float(row["std"])
            n_seeds = int(row["n_seeds"])

            data[(task, metric)] = {"mean": mean, "std": std, "n_seeds": n_seeds}

    return data


def load_postqlora(path: Path) -> list[dict]:
    # Keep post rows as a list and sort deterministically before writing outputs.
    records: list[dict] = []

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "adapter": row["adapter"],
                    "task": row["task"],
                    "metric": row["metric"],
                    "mean": float(row["mean"]),
                    "std": float(row["std"]),
                    "n_seeds": int(row["n_seeds"]),
                }
            )

    return records


def main() -> None:
    # Resolve repo root from this script path to make it runnable from any working directory.
    project_root = Path(__file__).resolve().parents[1]

    baseline_path = project_root / "evals" / "baseline" / "summary_preqlora_aggregated.csv"
    postqlora_path = project_root / "evals" / "postqlora" / "summary_postqlora_aggregated.csv"
    output_path = project_root / "evals" / "comparison" / "summary_pre_post_aggregated_all_adapters.csv"

    if not baseline_path.is_file():
        raise FileNotFoundError(f"Missing baseline summary CSV: {baseline_path}")
    if not postqlora_path.is_file():
        raise FileNotFoundError(f"Missing post-QLoRA summary CSV: {postqlora_path}")

    print(f"[compare_pre_post] baseline_summary   = {baseline_path}")
    print(f"[compare_pre_post] postqlora_summary  = {postqlora_path}")
    print(f"[compare_pre_post] comparison_output  = {output_path}")

    baseline = load_baseline(baseline_path)
    post_records = load_postqlora(postqlora_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "adapter",
        "task",
        "metric",
        "mean_pre",
        "std_pre",
        "n_seeds_pre",
        "mean_post",
        "std_post",
        "n_seeds_post",
        "delta",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for rec in sorted(post_records, key=lambda r: (r["adapter"], r["task"], r["metric"])):
            adapter = rec["adapter"]
            task = rec["task"]
            metric = rec["metric"]

            # Align TruthfulQA HR metric naming across pre/post.
            baseline_metric = "HR_TQA_pre" if (task == "truthfulqa_mc2" and metric == "HR_TQA_post") else metric

            key = (task, baseline_metric)
            if key not in baseline:
                print(
                    "[compare_pre_post] Warning: missing baseline entry for "
                    f"task={task}, metric={baseline_metric}. Skipping."
                )
                continue

            b = baseline[key]

            mean_pre = b["mean"]
            std_pre = b["std"]
            n_seeds_pre = b["n_seeds"]

            mean_post = rec["mean"]
            std_post = rec["std"]
            n_seeds_post = rec["n_seeds"]

            delta = mean_post - mean_pre

            writer.writerow(
                {
                    "adapter": adapter,
                    "task": task,
                    "metric": metric,
                    "mean_pre": mean_pre,
                    "std_pre": std_pre,
                    "n_seeds_pre": n_seeds_pre,
                    "mean_post": mean_post,
                    "std_post": std_post,
                    "n_seeds_post": n_seeds_post,
                    "delta": delta,
                }
            )

    print(f"[compare_pre_post] Comparison written to: {output_path}")


if __name__ == "__main__":
    main()
