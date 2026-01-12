#!/usr/bin/env python3
"""
Summarize post-QLoRA (multi-adapter) lm-eval-harness runs.

Purpose:
- Read lm-eval aggregated results JSON files under evals/postqlora/.
- Export per-seed and aggregated CSV summaries for all configured adapters.

Inputs (latest by mtime):
- evals/postqlora/postqlora_<task>_seed<seed>/*<adapter-fragment>*/results_*.json

Outputs:
- evals/postqlora/summary_postqlora_per_seed.csv
- evals/postqlora/summary_postqlora_aggregated.csv

Conventions:
- Tasks: truthfulqa_mc2, arc_easy
- Seeds: [0, 1, 2]
- Metrics:
  - truthfulqa_mc2: acc, HR_TQA_post = 1 - acc
  - arc_easy: acc, acc_norm

Determinism / reruns:
- If multiple results_*.json exist for an adapter (reruns), we select the newest by mtime.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TASKS: list[str] = ["truthfulqa_mc2", "arc_easy"]
SEEDS: list[int] = [0, 1, 2]

ADAPTERS: list[str] = ["alpaca_1k", "alpaca_10k", "alpaca_full", "dolly_5k", "dolly_full"]

# Logical adapter name -> distinctive lm-eval model_dir fragment
ADAPTER_SUBDIR_FRAGMENT: Dict[str, str] = {
    "alpaca_1k": "qwen3-8b-base-qlora-alpaca-1k",
    "alpaca_10k": "qwen3-8b-base-qlora-alpaca-10k",
    "alpaca_full": "qwen3-8b-base-qlora-alpaca-full",
    "dolly_5k": "qwen3-8b-base-qlora-dolly-5k",
    "dolly_full": "qwen3-8b-base-qlora-dolly-full",
}


@dataclass
class MetricRecord:
    adapter: str
    task: str
    seed: int
    metric: str
    value: float
    stderr: Optional[float]


def _find_latest_results_json_optional(run_dir: Path, pattern: str, log_prefix: str) -> Optional[Path]:
    # Select newest file by mtime (robust for reruns) (multiple results_*.json).
    candidates = list(run_dir.glob(pattern))
    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime)

    if len(candidates) > 1:
        print(
            f"{log_prefix} Note: {run_dir} has {len(candidates)} results_*.json for pattern '{pattern}'; "
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
    evals_dir = project_root / "evals" / "postqlora"
    records: List[MetricRecord] = []

    for adapter in ADAPTERS:
        fragment = ADAPTER_SUBDIR_FRAGMENT[adapter]

        for seed in SEEDS:
            for task in TASKS:
                run_dir = evals_dir / f"postqlora_{task}_seed{seed}"
                if not run_dir.exists():
                    print(f"[summarize_postqlora] Warning: {run_dir} does not exist, skipping.")
                    continue

                results_path = _find_latest_results_json_optional(
                    run_dir=run_dir,
                    pattern=f"*{fragment}*/results_*.json",
                    log_prefix="[summarize_postqlora]",
                )
                if results_path is None:
                    print(
                        f"[summarize_postqlora] Warning: no results_*.json found "
                        f"for adapter='{adapter}' under {run_dir}, skipping."
                    )
                    continue

                print(
                    f"[summarize_postqlora] Reading results from {results_path} "
                    f"(adapter={adapter}, task={task}, seed={seed})"
                )

                with results_path.open("r", encoding="utf-8") as f:
                    results_json = json.load(f)

                metrics_dict = _get_task_metrics_dict(results_json, task)

                if task == "truthfulqa_mc2":
                    acc, acc_stderr = _get_metric_value(metrics_dict, "acc")
                    records.append(MetricRecord(adapter=adapter, task=task, seed=seed, metric="acc", value=acc, stderr=acc_stderr))

                    hr_post = 1.0 - acc
                    records.append(MetricRecord(adapter=adapter, task=task, seed=seed, metric="HR_TQA_post", value=hr_post, stderr=None))

                elif task == "arc_easy":
                    acc, acc_stderr = _get_metric_value(metrics_dict, "acc")
                    records.append(MetricRecord(adapter=adapter, task=task, seed=seed, metric="acc", value=acc, stderr=acc_stderr))

                    acc_norm, acc_norm_stderr = _get_metric_value(metrics_dict, "acc_norm")
                    records.append(MetricRecord(adapter=adapter, task=task, seed=seed, metric="acc_norm", value=acc_norm, stderr=acc_norm_stderr))

                else:
                    print(f"[summarize_postqlora] Warning: task '{task}' is not handled by the metric logic.")

    return records


def _write_per_seed_csv(records: Iterable[MetricRecord], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["adapter", "task", "seed", "metric", "value", "stderr"]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "adapter": rec.adapter,
                    "task": rec.task,
                    "seed": rec.seed,
                    "metric": rec.metric,
                    "value": rec.value,
                    "stderr": rec.stderr if rec.stderr is not None else "",
                }
            )
    print(f"[summarize_postqlora] Wrote per-seed → {out_path}")


def _write_aggregated_csv(records: Iterable[MetricRecord], out_path: Path) -> None:
    # Aggregate across seeds: mean and (sample) standard deviation per (adapter, task, metric).
    from collections import defaultdict
    import math

    out_path.parent.mkdir(parents=True, exist_ok=True)

    grouped: Dict[Tuple[str, str, str], List[float]] = defaultdict(list)
    for rec in records:
        grouped[(rec.adapter, rec.task, rec.metric)].append(rec.value)

    fieldnames = ["adapter", "task", "metric", "mean", "std", "n_seeds"]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for (adapter, task, metric), values in sorted(grouped.items()):
            n = len(values)
            if n == 0:
                continue
            mean = sum(values) / n
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
            writer.writerow({"adapter": adapter, "task": task, "metric": metric, "mean": mean, "std": std, "n_seeds": n})

    print(f"[summarize_postqlora] Wrote aggregated → {out_path}")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    evals_dir = project_root / "evals" / "postqlora"

    print(f"[summarize_postqlora] project_root={project_root}")
    print(f"[summarize_postqlora] evals_dir={evals_dir}")

    records = _gather_per_seed_records(project_root)

    _write_per_seed_csv(records, evals_dir / "summary_postqlora_per_seed.csv")
    _write_aggregated_csv(records, evals_dir / "summary_postqlora_aggregated.csv")

    print("[summarize_postqlora] Done.")


if __name__ == "__main__":
    main()
