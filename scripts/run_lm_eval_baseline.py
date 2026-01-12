"""
scripts/run_lm_eval_baseline.py

Purpose:
- Run baseline (pre-QLoRA) evaluation with lm-eval-harness for a fixed task set and seeds.

Inputs:
- MODEL_PATH (env var): local Hugging Face model directory (e.g., Qwen3-8B-Base)

Evaluation protocol:
- tasks: truthfulqa_mc2, arc_easy
- seeds: [0, 1, 2] (passed as "seed,seed,seed,seed" for python/numpy/torch/fewshot)
- 0-shot: num_fewshot=0
- batch_size: auto with max_batch_size=4
- quantization: 4-bit NF4 + double quant + bf16 compute

Outputs:
- evals/baseline/baseline_{task}_seed{seed}/... (lm-eval output layout)
  - results_*.json (aggregated metrics)
  - samples_*.jsonl (per-item logs, used for bootstrap/McNemar/qualitative)

Notes:
- sys.executable ensures we run lm-eval inside the same venv as this script.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


TASKS = ["truthfulqa_mc2", "arc_easy"]
SEEDS = [0, 1, 2]


def get_model_path() -> str:
    # Read base model path from environment to avoid hardcoding machine-specific paths.
    model_path: Optional[str] = os.environ.get("MODEL_PATH")
    if not model_path:
        raise RuntimeError(
            "Environment variable MODEL_PATH is not set.\n"
            "Example:\n"
            "  export MODEL_PATH=/home/USER/models/qwen3-8b-base/Qwen3-8B-Base"
        )
    return model_path


def run_lm_eval_for_task_and_seed(
    *,
    model_path: str,
    task: str,
    seed: int,
    evals_dir: Path,
) -> None:
    # One output directory per (task, seed) for reproducibility and clean diffs.
    output_prefix = evals_dir / f"baseline_{task}_seed{seed}"

    # lm-eval HF model_args.
    model_args = (
        f"pretrained={model_path},"
        f"tokenizer={model_path},"
        "trust_remote_code=True,"
        "load_in_4bit=True,"
        "bnb_4bit_quant_type=nf4,"
        "bnb_4bit_use_double_quant=True,"
        "bnb_4bit_compute_dtype=bfloat16,"
        "dtype=bfloat16"
    )

    cmd: Sequence[str] = [
        sys.executable,
        "-m",
        "lm_eval",
        "--model",
        "hf",
        "--model_args",
        model_args,
        "--tasks",
        task,
        "--num_fewshot",
        "0",
        "--batch_size",
        "auto",
        "--max_batch_size",
        "4",
        "--seed",
        f"{seed},{seed},{seed},{seed}",
        "--output_path",
        str(output_prefix),
        "--log_samples",
    ]

    print(f"[run_lm_eval_baseline] Running task={task}, seed={seed}")
    print("  Command:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    evals_dir = project_root / "evals" / "baseline"
    evals_dir.mkdir(parents=True, exist_ok=True)

    model_path = get_model_path()
    print(f"[run_lm_eval_baseline] MODEL_PATH={model_path}")
    print(f"[run_lm_eval_baseline] evals_dir={evals_dir}")

    for seed in SEEDS:
        for task in TASKS:
            run_lm_eval_for_task_and_seed(
                model_path=model_path,
                task=task,
                seed=seed,
                evals_dir=evals_dir,
            )

    print("[run_lm_eval_baseline] Baseline evaluation completed (if no errors occurred).")


if __name__ == "__main__":
    main()
