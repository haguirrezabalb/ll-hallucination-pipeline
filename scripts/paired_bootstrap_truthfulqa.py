#!/usr/bin/env python3
"""
Paired bootstrap for TruthfulQA_mc2 (MC2 acc_i) using lm-eval-harness per-sample logs.

Goal:
- Provide a paired CI for Delta_acc (MC2) and Delta_HR_TQA, where HR = 1 - acc.
- Delta_HR_TQA = HR_TQA_post - HR_TQA_pre = -(acc_post - acc_pre) = -Delta_acc.

Design:
- Use paired per-item values aligned by doc_id.
- Bootstrap resamples doc_ids WITH replacement and computes the mean of Delta_acc.
- CI is percentile-based (default 95%).

Outputs:
- A CSV with one row per adapter, including Delta_acc mean + CI, and Delta_HR_TQA mean + CI.
- Baseline/post sample filenames are stored as basenames to avoid leaking local paths.

Example of typical execution :
  uv run python scripts/paired_bootstrap_truthfulqa.py \
    --seed 0 \
    --adapters alpaca_1k alpaca_10k alpaca_full dolly_5k dolly_full \
    --out_csv evals/comparison/paired_bootstrap_truthfulqa_mc2_seed0.csv
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


def newest_matching(pattern: str) -> str:
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No files match pattern: {pattern}")
    return max(matches, key=lambda p: os.path.getmtime(p))


def load_metric_by_doc_id(samples_path: str, metric: str) -> Dict[int, float]:
    """
    Loads a samples_*.jsonl file and returns {doc_id: metric_value}.
    Tries:
      - metric (e.g., "acc")
      - f"{metric},none" fallback
    """
    out: Dict[int, float] = {}
    with open(samples_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)

            if "doc_id" not in ex:
                raise ValueError(f"{samples_path}:{line_no} missing doc_id")
            did = int(ex["doc_id"])

            if metric in ex:
                val = ex[metric]
            else:
                alt = f"{metric},none"
                if alt in ex:
                    val = ex[alt]
                else:
                    raise KeyError(
                        f"{samples_path}:{line_no} missing metric '{metric}' "
                        f"(and fallback '{alt}')"
                    )

            out[did] = float(val)

    if not out:
        raise ValueError(f"No samples loaded from: {samples_path}")
    return out


def find_baseline_samples(baseline_root: str, task: str, seed: int) -> str:
    pattern = f"{baseline_root}/baseline_{task}_seed{seed}/*/samples_{task}_*.jsonl"
    return newest_matching(pattern)


def find_post_samples(post_by_adapter_root: str, adapter: str, task: str, seed: int) -> str:
    pattern = f"{post_by_adapter_root}/{adapter}/{task}_seed{seed}/samples_{task}_*.jsonl"
    return newest_matching(pattern)


def paired_deltas(pre: Dict[int, float], post: Dict[int, float]) -> np.ndarray:
    common = sorted(set(pre.keys()) & set(post.keys()))
    if not common:
        raise ValueError("No common doc_id keys between pre and post samples.")
    deltas = np.array([post[d] - pre[d] for d in common], dtype=np.float64)
    return deltas


def bootstrap_mean_ci(
    deltas: np.ndarray,
    n_boot: int,
    seed: int,
    alpha: float,
) -> Tuple[float, float, float]:
    # Percentile CI for mean(deltas) via paired bootstrap.
    # Returns (mean, ci_low, ci_high).
    rng = np.random.default_rng(seed)
    n = deltas.shape[0]
    idx = rng.integers(0, n, size=(n_boot, n), endpoint=False)
    boot_means = deltas[idx].mean(axis=1)

    mean = float(deltas.mean())
    low = float(np.quantile(boot_means, alpha / 2.0))
    high = float(np.quantile(boot_means, 1.0 - alpha / 2.0))
    return mean, low, high

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Paired bootstrap CI for TruthfulQA_mc2 deltas (acc_i and HR_TQA).")
    p.add_argument("--seed", type=int, default=0, help="evaluation seed to use (default: 0)")
    p.add_argument("--task", default="truthfulqa_mc2", help="lm-eval task name (default: truthfulqa_mc2)")
    p.add_argument("--metric", default="acc", help="metric key in samples (default: acc for MC2 score)")
    p.add_argument("--baseline_root", default="evals/baseline", help="baseline root directory")
    p.add_argument("--post_by_adapter_root", default="evals/postqlora/by_adapter", help="post root by_adapter directory")

    p.add_argument(
        "--adapters",
        nargs="*",
        default=None,
        help="adapters to evaluate (default: autodetect directories under post_by_adapter_root)",
    )

    p.add_argument("--n_boot", type=int, default=10000, help="number of bootstrap resamples (default: 10000)")
    p.add_argument("--bootstrap_seed", type=int, default=123, help="RNG seed for bootstrap (default: 123)")
    p.add_argument("--alpha", type=float, default=0.05, help="alpha for CI (default: 0.05 => 95%% CI)")

    p.add_argument(
        "--out_csv",
        default=None,
        help="output CSV path (default: evals/comparison/paired_bootstrap_<task>_seed<seed>.csv)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    task = args.task
    seed = args.seed
    metric = args.metric

    baseline_root = args.baseline_root
    post_root = args.post_by_adapter_root

    # Detect adapters if not provided
    if args.adapters is None or len(args.adapters) == 0:
        post_root_path = Path(post_root)
        adapters = sorted([p.name for p in post_root_path.iterdir() if p.is_dir()])
        if not adapters:
            raise RuntimeError(f"No adapter directories found under: {post_root}")
    else:
        adapters = list(args.adapters)

    out_csv = args.out_csv or f"evals/comparison/paired_bootstrap_{task}_seed{seed}.csv"
    out_csv_path = Path(out_csv)
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)

    baseline_samples = find_baseline_samples(baseline_root, task, seed)
    pre_map = load_metric_by_doc_id(baseline_samples, metric)

    rows: List[dict] = []

    print(f"[INFO] task={task} seed={seed} metric={metric}")
    print(f"[INFO] baseline_samples={os.path.basename(baseline_samples)}")
    print(f"[INFO] n_boot={args.n_boot} bootstrap_seed={args.bootstrap_seed} alpha={args.alpha}")
    print()

    for adapter in adapters:
        post_samples = find_post_samples(post_root, adapter, task, seed)
        post_map = load_metric_by_doc_id(post_samples, metric)

        deltas = paired_deltas(pre_map, post_map)
        n_items = int(deltas.shape[0])

        # Delta_acc = mean(post - pre)
        dacc_mean, dacc_lo, dacc_hi = bootstrap_mean_ci(
            deltas=deltas,
            n_boot=args.n_boot,
            seed=args.bootstrap_seed,
            alpha=args.alpha,
        )

        # Delta_HR_TQA = -Delta_acc (because HR = 1 - acc)
        dhr_mean = -dacc_mean
        # CI transforms similarly: negate endpoints and swap
        dhr_lo = -dacc_hi
        dhr_hi = -dacc_lo

        row = {
            "adapter": adapter,
            "task": task,
            "seed": seed,
            "metric": metric,
            "n_items": n_items,
            "delta_acc_mean": dacc_mean,
            "delta_acc_ci_low": dacc_lo,
            "delta_acc_ci_high": dacc_hi,
            "delta_hr_tqa_mean": dhr_mean,
            "delta_hr_tqa_ci_low": dhr_lo,
            "delta_hr_tqa_ci_high": dhr_hi,
            "n_boot": args.n_boot,
            "bootstrap_seed": args.bootstrap_seed,
            "baseline_samples": os.path.basename(baseline_samples),
            "post_samples": os.path.basename(post_samples),
        }
        rows.append(row)

        print(
            f"{adapter:>12} | n={n_items:4d} "
            f"Delta_acc={dacc_mean:+.6f} CI=[{dacc_lo:+.6f},{dacc_hi:+.6f}] | "
            f"Delta_HR_TQA={dhr_mean:+.6f} CI=[{dhr_lo:+.6f},{dhr_hi:+.6f}]"
        )

    # CSV
    fieldnames = list(rows[0].keys()) if rows else []
    with out_csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print()
    print(f"[OK] Wrote: {out_csv_path}")


if __name__ == "__main__":
    main()
