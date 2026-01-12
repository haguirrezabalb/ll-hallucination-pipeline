"""
scripts/run_lm_eval_postqlora.py

Purpose:
- Run post-QLoRA evaluation with lm-eval-harness for a fixed task set and seeds.

Inputs:
- MODEL_PATH (env var): base model directory (same as baseline)
- LORA_ADAPTER_PATH (env var): PEFT adapter directory containing adapter_config.json (+ adapter weights)

Evaluation protocol:
- tasks: truthfulqa_mc2, arc_easy
- seeds: [0, 1, 2] (passed as "seed,seed,seed,seed" for python/numpy/torch/fewshot)
- 0-shot: num_fewshot=0
- batch_size: auto with max_batch_size=4
- quantization: 4-bit NF4 + double quant + bf16 compute
- PEFT: load adapter via model_args "peft=<path>"

Outputs:
- evals/postqlora/postqlora_{task}_seed{seed}/... (lm-eval output layout)
  - results_*.json (aggregated metrics)
  - samples_*.jsonl (per-item logs)

Notes:
- tokenizer is set to MODEL_PATH (not the adapter dir) to keep tokenizer/model consistent.
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


def get_lora_adapter_path() -> str:
    """
    Return the path to a trained LoRA adapter directory.

    LORA_ADAPTER_PATH must point to a PEFT adapter directory containing:
    - adapter_config.json
    - adapter_model.* (e.g., safetensors)
    """
    lora_path: Optional[str] = os.environ.get("LORA_ADAPTER_PATH")
    if not lora_path:
        raise RuntimeError(
            "Environment variable LORA_ADAPTER_PATH is not set.\n"
            "Example:\n"
            "  export LORA_ADAPTER_PATH=$HOME/models/qwen3-8b-base-qlora-alpaca-full\n"
            "The path must be a PEFT adapter directory containing adapter_config.json.\n"
        )

    lora_dir = Path(lora_path).expanduser()
    adapter_config_path = lora_dir / "adapter_config.json"
    if not adapter_config_path.is_file():
        raise RuntimeError(
            "LORA_ADAPTER_PATH does not point to a valid PEFT adapter directory.\n"
            f"Missing file: {adapter_config_path}\n"
            "Make sure the directory contains adapter_config.json and adapter_model.safetensors.\n"
        )

    return str(lora_dir)


def run_lm_eval_for_task_and_seed(
    *,
    model_path: str,
    lora_adapter_path: str,
    task: str,
    seed: int,
    evals_dir: Path,
) -> None:
    # One output directory per (task, seed) for reproducibility and clean diffs.
    output_prefix = evals_dir / f"postqlora_{task}_seed{seed}"

    # lm-eval HF model_args:
    # - load the PEFT adapter via peft=<dir>
    model_args = (
        f"pretrained={model_path},"
        f"tokenizer={model_path},"
        "trust_remote_code=True,"
        "load_in_4bit=True,"
        "bnb_4bit_quant_type=nf4,"
        "bnb_4bit_use_double_quant=True,"
        "bnb_4bit_compute_dtype=bfloat16,"
        "dtype=bfloat16,"
        f"peft={lora_adapter_path}"
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

    print(f"[run_lm_eval_postqlora] Running task={task}, seed={seed}")
    print("  Command:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    evals_dir = project_root / "evals" / "postqlora"
    evals_dir.mkdir(parents=True, exist_ok=True)

    model_path = get_model_path()
    lora_adapter_path = get_lora_adapter_path()

    print(f"[run_lm_eval_postqlora] MODEL_PATH={model_path}")
    print(f"[run_lm_eval_postqlora] LORA_ADAPTER_PATH={lora_adapter_path}")
    print(f"[run_lm_eval_postqlora] evals_dir={evals_dir}")

    for seed in SEEDS:
        for task in TASKS:
            run_lm_eval_for_task_and_seed(
                model_path=model_path,
                lora_adapter_path=lora_adapter_path,
                task=task,
                seed=seed,
                evals_dir=evals_dir,
            )

    print("[run_lm_eval_postqlora] Post-QLoRA evaluation completed (if no errors occurred).")


if __name__ == "__main__":
    main()
