#!/usr/bin/env python3
"""
scripts/export_delta_summary_for_plots.py

Purpose:
- Export a minimal, stable CSV with the key deltas needed for downstream plotting.

Inputs:
- evals/comparison/summary_pre_post_aggregated_all_adapters.csv
  (produced by scripts/compare_pre_post.py)

Outputs:
- evals/comparison/delta_summary_for_plots.csv

Output schema:
- adapter
- delta_hr_truthfulqa      (ΔHR_TQA = HR_post - HR_pre, lower is better)
- delta_acc_norm_arc       (Δacc_norm on ARC-Easy, higher is better)

Notes:
- TruthfulQA uses HR_TQA_post as the hallucination-rate proxy (HR_TQA = 1 - acc(MC2)).
- ARC uses acc_norm as the utility proxy.

Determinism / reruns:
- Adapter order is fixed by default to keep plots stable across runs.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Tuple


# Fixed display order for plots/tables (keeps figure annotations stable).
DEFAULT_ADAPTERS = ["alpaca_1k", "alpaca_10k", "alpaca_full", "dolly_5k", "dolly_full"]


def load_rows(path: Path) -> list[dict]:
    # Load the comparison CSV as a list of dict rows.
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_index(rows: list[dict]) -> Dict[Tuple[str, str, str], dict]:
    # Build an index for O(1) lookup by (adapter, task, metric).
    idx: Dict[Tuple[str, str, str], dict] = {}
    for r in rows:
        idx[(r["adapter"], r["task"], r["metric"])] = r
    return idx


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a small delta summary CSV for plotting.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("evals/comparison/summary_pre_post_aggregated_all_adapters.csv"),
        help="Path to the aggregated pre/post comparison CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evals/comparison/delta_summary_for_plots.csv"),
        help="Path to the output delta summary CSV.",
    )
    parser.add_argument(
        "--adapters",
        nargs="*",
        default=DEFAULT_ADAPTERS,
        help="Adapter order to export (default: a fixed, consistent order).",
    )
    args = parser.parse_args()

    # Read and index the pre/post comparison table.
    rows = load_rows(args.input)
    idx = build_index(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["adapter", "delta_hr_truthfulqa", "delta_acc_norm_arc"])

        for a in args.adapters:
            # Keys correspond to rows produced by scripts/compare_pre_post.py.
            hr_key = (a, "truthfulqa_mc2", "HR_TQA_post")
            arc_key = (a, "arc_easy", "acc_norm")

            if hr_key not in idx:
                raise KeyError(f"Missing row for {hr_key} in {args.input}")
            if arc_key not in idx:
                raise KeyError(f"Missing row for {arc_key} in {args.input}")

            # The comparison CSV stores deltas as strings; parse and export with fixed precision.
            d_hr = float(idx[hr_key]["delta"])
            d_accn = float(idx[arc_key]["delta"])
            w.writerow([a, f"{d_hr:.6f}", f"{d_accn:.6f}"])

    print(f"[export_delta_summary_for_plots] Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
