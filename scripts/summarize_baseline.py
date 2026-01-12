#!/usr/bin/env python3
"""
Summarize baseline (pre-QLoRA) lm-eval-harness runs.

Purpose:
- Read lm-eval aggregated results JSON files under evals/baseline/.
- Export per-seed and aggregated CSV summaries used by downstream scripts.

Inputs (latest by mtime):
- evals/baseline/baseline_<task>_seed<seed>/*/results_*.json

Outputs:
- evals/baseline/summary_preqlora_per_seed.csv
- evals/baseline/summary_preqlora_aggregated.csv

Conventions:
- Tasks: truthfulqa_mc2, arc_easy
- Seeds: [0, 1, 2]
- Metrics:
  - truthfulqa_mc2: acc, HR_TQA_pre = 1 - acc
  - arc_easy: acc, acc_norm

Determinism / reruns:
- If multiple results_*.json exist (reruns), we select the newest by mtime.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TASKS: list[str] = ["truthfulqa_mc2", "arc_easy"]
SEEDS: list[int] = [0, 1, 2]


@dataclass
class MetricRecord:
    task: str
    seed: int
    metric: str
    value: float
    stderr: Optional[float]


def _find_latest_results_json(run_dir: Path, pattern: str, log_prefix: str) -> Path:
    # Select newest file by mtime (robust for reruns) (multiple results_*.json).
    candidates = list(run_dir.glob(pattern))
    if not candidates:
        raise FileNotFoundError(f"No results_*.json found under {run_dir}")

    candidates.sort(key=lambda p: p.stat().st_mtime)

    if len(candidates) > 1:
        print(
            f"{log_prefix} Note: {run_dir} has {len(candidates)} results_*.json; "
            f"using latest by mtime: {candidates[-1].name}"
        )

    return candidates[-1]


def _get_task_metrics_dict(results_json: Dict[str, Any], task: str) -> Dict[str, Any]:
    results = results_json.get("results", {})
    if task not in results:
        raise KeyError(f"Task '{task}' not found in results JSON. Keys: {list(results.keys())}")
    return results[task]


def _get_metric_value(metrics_dict: Dict[str, Any], metric_base: str) -> Tuple[float, Optional[float]]:
    # Return (value, stderr) for a base metric ('acc', 'acc_norm', etc.)
    # while tolerating key variants:
    #   - 'acc' / 'acc_stderr'
    #   - 'acc,none' / 'acc_stderr,none'

    # Value key
    val_key: Optional[str] = None
    if metric_base in metrics_dict:
        val_key = metric_base
    else:
        for key in metrics_dict:
            if key.startswith(metric_base + ","):
                val_key = key
                break
    if val_key is None:
        raise KeyError(f"No key found for metric '{metric_base}' in {list(metrics_dict.keys())}")
    value = float(metrics_dict[val_key])

    # stderr key (optional)
    stderr_base = metric_base + "_stderr"
    stderr_key: Optional[str] = None
    if stderr_base in metrics_dict:
        stderr_key = stderr_base
    else:
        for key in metrics_dict:
            if key.startswith(stderr_base + ","):
                stderr_key = key
                break

    stderr = float(metrics_dict[stderr_key]) if stderr_key is not None else None
    return value, stderr


def _gather_per_seed_records(project_root: Path) -> List[MetricRecord]:
    evals_dir = project_root / "evals" / "baseline"
    records: List[MetricRecord] = []

    for seed in SEEDS:
        for task in TASKS:
            run_dir = evals_dir / f"baseline_{task}_seed{seed}"
            if not run_dir.exists():
                print(f"[summarize_baseline] Warning: {run_dir} does not exist, skipping.")
                continue

            results_path = _find_latest_results_json(
                run_dir=run_dir,
                pattern="*/results_*.json",
                log_prefix="[summarize_baseline]",
            )
            print(f"[summarize_baseline] Reading results from {results_path}")

            with results_path.open("r", encoding="utf-8") as f:
                results_json = json.load(f)

            metrics_dict = _get_task_metrics_dict(results_json, task)

            if task == "truthfulqa_mc2":
                acc, acc_stderr = _get_metric_value(metrics_dict, "acc")
                records.append(MetricRecord(task=task, seed=seed, metric="acc", value=acc, stderr=acc_stderr))

                hr_pre = 1.0 - acc
                records.append(MetricRecord(task=task, seed=seed, metric="HR_TQA_pre", value=hr_pre, stderr=None))

            elif task == "arc_easy":
                acc, acc_stderr = _get_metric_value(metrics_dict, "acc")
                records.append(MetricRecord(task=task, seed=seed, metric="acc", value=acc, stderr=acc_stderr))

                acc_norm, acc_norm_stderr = _get_metric_value(metrics_dict, "acc_norm")
                records.append(
                    MetricRecord(task=task, seed=seed, metric="acc_norm", value=acc_norm, stderr=acc_norm_stderr)
                )

            else:
                print(f"[summarize_baseline] Warning: task '{task}' is not handled by the metric logic.")

    return records


def _write_per_seed_csv(records: Iterable[MetricRecord], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["task", "seed", "metric", "value", "stderr"]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "task": rec.task,
                    "seed": rec.seed,
                    "metric": rec.metric,
                    "value": rec.value,
                    "stderr": rec.stderr if rec.stderr is not None else "",
                }
            )
    print(f"[summarize_baseline] Wrote per-seed → {out_path}")


def _write_aggregated_csv(records: Iterable[MetricRecord], out_path: Path) -> None:
    # Aggregate across seeds: mean and (sample) standard deviation per (task, metric).
    from collections import defaultdict
    import math

    out_path.parent.mkdir(parents=True, exist_ok=True)

    grouped: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    for rec in records:
        grouped[(rec.task, rec.metric)].append(rec.value)

    fieldnames = ["task", "metric", "mean", "std", "n_seeds"]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (task, metric), values in sorted(grouped.items()):
            n = len(values)
            if n == 0:
                continue
            mean = sum(values) / n
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0

            writer.writerow({"task": task, "metric": metric, "mean": mean, "std": std, "n_seeds": n})

    print(f"[summarize_baseline] Wrote aggregated → {out_path}")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    evals_dir = project_root / "evals" / "baseline"

    print(f"[summarize_baseline] project_root={project_root}")
    print(f"[summarize_baseline] evals_dir={evals_dir}")

    records = _gather_per_seed_records(project_root)

    _write_per_seed_csv(records, evals_dir / "summary_preqlora_per_seed.csv")
    _write_aggregated_csv(records, evals_dir / "summary_preqlora_aggregated.csv")

    print("[summarize_baseline] Done.")


if __name__ == "__main__":
    main()
