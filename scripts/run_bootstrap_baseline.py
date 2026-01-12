#!/usr/bin/env python3
"""
scripts/run_bootstrap_baseline.py

Purpose:
- Walk evals/baseline/ and compute a bootstrap mean and confidence interval for each (task, seed)
  from lm-eval-harness per-sample logs (samples_*.jsonl).

Inputs:
- evals/baseline/baseline_<task>_seed<seed>/*/samples_*.jsonl (latest by mtime per run)

Outputs:
- Prints a CSV-like table to stdout:
    task,seed,n,empirical_mean,ci_lo,ci_hi

Notes:
- Uses bootstrap_mc_accuracy.py utilities:
  - load_samples(): loads is_correct or acc into numeric values
  - accuracy(): empirical mean of the per-item metric
  - bootstrap_accuracy(): percentile CI over bootstrap replicate means
- Bootstrap settings are fixed here: iters=20000, seed=0.

Determinism / reruns:
- For each run directory, the newest samples_*.jsonl by mtime is selected (rerun-safe).
- Bootstrap is deterministic given seed=0.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from bootstrap_mc_accuracy import accuracy, bootstrap_accuracy, load_samples


BASELINE_DIR = Path(__file__).resolve().parents[1] / "evals" / "baseline"


def find_sample_files() -> List[Tuple[str, int, Path]]:
    # Walk evals/baseline and return (task, seed, samples_jsonl_path) tuples.
    items: List[Tuple[str, int, Path]] = []

    for run_dir in BASELINE_DIR.iterdir():
        if not run_dir.is_dir():
            continue

        name = run_dir.name
        if not name.startswith("baseline_"):
            continue

        seed_tag = "_seed"
        if seed_tag not in name:
            continue

        # Extract task between "baseline_" and "_seed<k>".
        prefix = "baseline_"
        task = name[len(prefix) : name.rfind(seed_tag)]

        # Extract seed from the suffix "seed<k>".
        seed_str = name[name.rfind(seed_tag) + 1 :]  # e.g., "seed0"
        if not seed_str.startswith("seed"):
            continue

        try:
            seed = int(seed_str.replace("seed", ""))
        except ValueError:
            continue

        # lm-eval creates a model_dir nested under the run dir; take the first directory found.
        subdirs = [d for d in run_dir.iterdir() if d.is_dir()]
        if not subdirs:
            continue
        model_dir = subdirs[0]

        sample_files = list(model_dir.glob("samples_*.jsonl"))
        if not sample_files:
            continue

        # Select newest samples file by mtime to be robust to reruns.
        latest = max(sample_files, key=lambda p: p.stat().st_mtime)
        items.append((task, seed, latest))

    return items


def main() -> None:
    print("[run_bootstrap_baseline] Searching for samples in evals/baseline ...")
    items = find_sample_files()

    if not items:
        print("No samples_*.jsonl files were found.")
        return

    print(f"Found {len(items)} baseline runs\n")
    print("task,seed,n,mean,CI_lo,CI_hi")

    # Sort for stable output across runs/environments.
    for task, seed, path in sorted(items):
        samples = load_samples(path)
        n = len(samples)
        base_mean = accuracy(samples)

        # Fixed bootstrap settings (kept stable for reproducibility).
        _, lo, hi = bootstrap_accuracy(samples, iters=20000, seed=0)

        print(f"{task},{seed},{n},{base_mean:.6f},{lo:.6f},{hi:.6f}")


if __name__ == "__main__":
    main()
