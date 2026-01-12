#!/usr/bin/env python3
"""
McNemar exact test from lm-eval-harness per-sample logs (samples_*.jsonl).

Primary use in this project:
- Task: arc_easy
- Metric: acc_norm (binary per item)
- Compare baseline vs post-QLoRA adapters using evals/postqlora/by_adapter/

It:
- Finds the latest samples file for baseline and each adapter.
- Aligns items by doc_id.
- Builds the 2x2 table counts (n00,n01,n10,n11) for a binary metric.
- Computes exact McNemar p-value via a two-sided binomial test (p=0.5).
- Writes a CSV suitable to fill the thesis table.
- Optionally saves a plot (n01 vs n10 per adapter).

Run example:
  uv run python scripts/mcnemar_from_samples.py \
    --task arc_easy --seed 0 --metric acc_norm \
    --adapters alpaca_1k alpaca_10k alpaca_full dolly_5k dolly_full \
    --out_csv evals/comparison/mcnemar_arc_easy_seed0.csv \
    --plot_path docs/figures/mcnemar_arc_easy_seed0.png
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def newest_matching(pattern: str) -> str:
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(f"No files match pattern: {pattern}")
    return max(matches, key=lambda p: os.path.getmtime(p))


def load_metric_by_doc_id(samples_path: str, metric: str) -> Dict[int, float]:
    # Loads a samples_*.jsonl file and returns {doc_id: metric_value}.
    # Assumes:
    #  - Each line is a JSON object with at least 'doc_id' and the metric key
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

            # Metric can be stored directly as a top-level key
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


def binarize(x: float, threshold: float = 0.5) -> int:
    return 1 if x >= threshold else 0


def log_comb(n: int, k: int) -> float:
    # log(C(n,k)) using lgamma for stability
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def logsumexp(logps: Iterable[float]) -> float:
    logps = list(logps)
    m = max(logps)
    return m + math.log(sum(math.exp(lp - m) for lp in logps))


def binom_cdf_half(n: int, k: int) -> float:
    # P(X <= k) for X ~ Binom(n, 0.5), computed stably via log-sum-exp.
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    ln2 = math.log(2.0)
    logps = [log_comb(n, i) - n * ln2 for i in range(0, k + 1)]
    return math.exp(logsumexp(logps))


def mcnemar_exact_p(n01: int, n10: int) -> float:
    # Two-sided exact McNemar p-value computed as:
    #   p = 2 * P(X <= min(n01, n10))  where X ~ Binom(n01+n10, 0.5)
    # Clipped to [0,1].
    n = n01 + n10
    if n == 0:
        return 1.0
    k = min(n01, n10)
    p = 2.0 * binom_cdf_half(n, k)
    return min(1.0, p)


def contingency_counts(
    pre: Dict[int, float],
    post: Dict[int, float],
    threshold: float,
) -> Tuple[int, int, int, int, int]:
    # Returns (n00, n01, n10, n11, n_common)
    # where first index is pre (0/1), second is post (0/1).
    common = sorted(set(pre.keys()) & set(post.keys()))
    n00 = n01 = n10 = n11 = 0
    for did in common:
        a = binarize(pre[did], threshold)
        b = binarize(post[did], threshold)
        if a == 0 and b == 0:
            n00 += 1
        elif a == 0 and b == 1:
            n01 += 1
        elif a == 1 and b == 0:
            n10 += 1
        else:
            n11 += 1
    return n00, n01, n10, n11, len(common)


def mean_binary_metric(values: Iterable[int]) -> float:
    vals = list(values)
    return (sum(vals) / len(vals)) if vals else float("nan")


def find_baseline_samples(baseline_root: str, task: str, seed: int) -> str:
    pattern = f"{baseline_root}/baseline_{task}_seed{seed}/*/samples_{task}_*.jsonl"
    return newest_matching(pattern)

def find_post_samples(post_by_adapter_root: str, adapter: str, task: str, seed: int) -> str:
    pattern = f"{post_by_adapter_root}/{adapter}/{task}_seed{seed}/samples_{task}_*.jsonl"
    return newest_matching(pattern)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="McNemar exact test from lm-eval samples_*.jsonl")
    p.add_argument("--task", default="arc_easy", help="lm-eval task name (default: arc_easy)")
    p.add_argument("--seed", type=int, default=0, help="seed to use (default: 0)")
    p.add_argument("--metric", default="acc_norm", help="binary metric key in samples (default: acc_norm)")
    p.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="threshold to binarize metric (default: 0.5)",
    )

    p.add_argument("--baseline_root", default="evals/baseline", help="baseline root directory")
    p.add_argument(
        "--post_by_adapter_root",
        default="evals/postqlora/by_adapter",
        help="post root by_adapter directory",
    )
    p.add_argument(
        "--adapters",
        nargs="*",
        default=None,
        help="adapters to evaluate (default: autodetect directories under post_by_adapter_root)",
    )

    p.add_argument(
        "--out_csv",
        default=None,
        help="output CSV path (default: evals/comparison/mcnemar_<task>_seed<seed>.csv)",
    )
    p.add_argument(
        "--plot_path",
        default=None,
        help="optional plot path (e.g., docs/figures/mcnemar_arc_easy_seed0.png)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    task = args.task
    seed = args.seed
    metric = args.metric
    threshold = args.threshold

    baseline_root = args.baseline_root
    post_root = args.post_by_adapter_root

    if args.adapters is None or len(args.adapters) == 0:
        # Detects adapters as directories inside by_adapter/
        post_root_path = Path(post_root)
        adapters = sorted([p.name for p in post_root_path.iterdir() if p.is_dir()])
        if not adapters:
            raise RuntimeError(f"No adapter directories found under: {post_root}")
    else:
        adapters = list(args.adapters)

    out_csv = args.out_csv or f"evals/comparison/mcnemar_{task}_seed{seed}.csv"
    out_csv_path = Path(out_csv)
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)

    baseline_samples = find_baseline_samples(baseline_root, task, seed)
    pre_map = load_metric_by_doc_id(baseline_samples, metric)

    rows: List[dict] = []

    print(f"[INFO] task={task} seed={seed} metric={metric} threshold={threshold}")
    print(f"[INFO] baseline_samples={os.path.basename(baseline_samples)}")
    print()

    for adapter in adapters:
        post_samples = find_post_samples(post_root, adapter, task, seed)
        post_map = load_metric_by_doc_id(post_samples, metric)

        n00, n01, n10, n11, n_common = contingency_counts(pre_map, post_map, threshold)
        discordant = n01 + n10
        pval = mcnemar_exact_p(n01, n10)

        # Compute empirical delta in mean (binary) metric over common items
        common = sorted(set(pre_map.keys()) & set(post_map.keys()))
        pre_bin = [binarize(pre_map[d], threshold) for d in common]
        post_bin = [binarize(post_map[d], threshold) for d in common]
        mean_pre = mean_binary_metric(pre_bin)
        mean_post = mean_binary_metric(post_bin)
        delta = mean_post - mean_pre

        row = {
            "adapter": adapter,
            "task": task,
            "seed": seed,
            "metric": metric,
            "n_items": n_common,
            "n00": n00,
            "n01": n01,
            "n10": n10,
            "n11": n11,
            "discordant": discordant,
            "mean_pre": mean_pre,
            "mean_post": mean_post,
            "delta": delta,
            "p_value_exact": pval,
            "baseline_samples": os.path.basename(baseline_samples),
            "post_samples": os.path.basename(post_samples),
        }
        rows.append(row)

        print(
            f"{adapter:>12} | n01={n01:4d} n10={n10:4d} n={discordant:4d} "
            f"p={pval:.6g} | delta={delta:+.6f}"
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

    # Plot
    if args.plot_path:
        plot_path = Path(args.plot_path)
        plot_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            raise RuntimeError(
                "matplotlib is required for --plot_path but could not be imported"
            ) from e

        labels = [r["adapter"] for r in rows]
        n01s = [r["n01"] for r in rows]
        n10s = [r["n10"] for r in rows]

        x = list(range(len(labels)))
        width = 0.4

        fig, ax = plt.subplots()
        ax.bar([i - width / 2 for i in x], n01s, width=width, label="n01 (pre 0 → post 1)")
        ax.bar([i + width / 2 for i in x], n10s, width=width, label="n10 (pre 1 → post 0)")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel("Count of items")
        ax.set_title(f"McNemar counts (task={task}, seed={seed}, metric={metric})")
        ax.legend()

        fig.tight_layout()
        fig.savefig(plot_path, dpi=200)
        print(f"[OK] Plot saved to: {plot_path}")


if __name__ == "__main__":
    main()
