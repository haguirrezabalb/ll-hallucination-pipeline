#!/usr/bin/env python3
"""
scripts/bootstrap_mc_accuracy.py

Purpose:
- Compute a bootstrap mean and confidence interval for a per-sample metric from
  lm-eval-harness per-sample logs (samples_*.jsonl).

Inputs:
- --samples: path to a samples_*.jsonl file produced by lm-eval-harness.

Outputs:
- Prints:
  - empirical mean of the per-item metric
  - bootstrap mean (mean of bootstrap replicate means)
  - 95% percentile CI

Notes:
- Supported per-item representations:
  - is_correct (bool) -> converted to 0/1
  - acc (float)       -> used as-is (e.g., MC2 probability mass for TruthfulQA_mc2)
- CI is a basic percentile CI (not BCa).

Determinism / reruns:
- Bootstrap is deterministic given --seed.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


@dataclass
class Sample:
    # Single scalar metric per item (typically in [0, 1]).
    value: float


def load_samples(path: Path) -> List[Sample]:
    """
    Load lm-eval-harness per-sample logs (JSONL).

    This loader supports two common representations:
    - "is_correct": boolean correctness flag (converted to 0/1)
    - "acc": a per-item score (float), e.g. MC2 probability mass on true options for TruthfulQA_mc2

    If neither key exists, we raise because downstream bootstrap requires a numeric per-item metric.
    """
    samples: List[Sample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            if "is_correct" in obj:
                v = 1.0 if bool(obj["is_correct"]) else 0.0
            elif "acc" in obj:
                v = float(obj["acc"])
            else:
                raise KeyError(
                    f"Neither 'is_correct' nor 'acc' was found in the sample. Keys={list(obj.keys())}"
                )

            samples.append(Sample(value=v))

    return samples


def accuracy(samples: Iterable[Sample]) -> float:
    # Compute the empirical mean of the per-item metric (works for binary or continuous values).
    xs = list(samples)
    if not xs:
        raise ValueError("No samples available to compute the mean")
    total = sum(s.value for s in xs)
    return total / len(xs)


def bootstrap_accuracy(samples: List[Sample], iters: int, seed: int) -> Tuple[float, float, float]:
    """
    Nonparametric bootstrap of the mean(value).

    - Resamples N items with replacement (N = len(samples)) for each iteration.
    - Computes the mean on each bootstrap resample.
    - Returns (bootstrap_mean, ci_low, ci_high) where ci_low/ci_high are a 95% percentile CI (2.5% / 97.5%).

    This is a basic percentile CI (not BCa). bootstrap_mean is the average of bootstrap replicate means.
    """
    if not samples:
        raise ValueError("No samples available for bootstrap")

    rng = random.Random(seed)
    n = len(samples)
    accs: List[float] = []

    for _ in range(iters):
        batch = [samples[rng.randrange(n)] for _ in range(n)]
        accs.append(accuracy(batch))

    accs.sort()
    mean = sum(accs) / len(accs)
    lo_idx = int(0.025 * (len(accs) - 1))
    hi_idx = int(0.975 * (len(accs) - 1))
    lo = accs[lo_idx]
    hi = accs[hi_idx]
    return mean, lo, hi


def parse_args() -> argparse.Namespace:
    # CLI wrapper (this script can be used standalone on any samples_*.jsonl).
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap the mean of a per-sample metric (e.g., accuracy) "
            "from lm-eval-harness samples_*.jsonl files"
        )
    )
    parser.add_argument("--samples", type=Path, required=True, help="Path to a samples_*.jsonl file")
    parser.add_argument("--iters", type=int, default=10000, help="Number of bootstrap iterations")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load per-item scores, compute empirical mean, and bootstrap CI.
    samples = load_samples(args.samples)
    base_acc = accuracy(samples)
    mean, lo, hi = bootstrap_accuracy(samples, args.iters, args.seed)

    print(f"samples: {len(samples)}")
    print(f"empirical mean: {base_acc:.6f}")
    print(f"bootstrap mean: {mean:.6f}")
    print(f"95% CI (percentile): [{lo:.6f}, {hi:.6f}]")


if __name__ == "__main__":
    main()
