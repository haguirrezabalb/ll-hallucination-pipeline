#!/usr/bin/env python3
"""
scripts/prepare_dolly_subsets.py

Purpose:
- Download `databricks/databricks-dolly-15k` from Hugging Face and export JSONL files
  compatible with train_qlora.py (instruction/input/output schema).

Inputs:
- Hugging Face dataset: databricks/databricks-dolly-15k (split="train")

Outputs:
- docs/datasets/dolly_15k.jsonl  (full set, deterministically shuffled)
- docs/datasets/dolly_5k.jsonl   (5k subset = prefix of the shuffled full set)

Schema (one JSON object per line):
- instruction <- Dolly "instruction"
- input       <- Dolly "context"
- output      <- Dolly "response"

Determinism / reruns:
- Shuffling is deterministic given RNG_SEED, and dolly_5k is a prefix of dolly_15k.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from datasets import load_dataset


DATASET_NAME = "databricks/databricks-dolly-15k"
OUTPUT_DIR = Path("docs") / "datasets"
RNG_SEED = 42


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[prepare_dolly_subsets] Loading dataset {DATASET_NAME} ...")
    ds = load_dataset(DATASET_NAME, split="train")
    print(f"[prepare_dolly_subsets] Total examples: {len(ds)}")
    print(f"[prepare_dolly_subsets] RNG_SEED: {RNG_SEED}")

    # Convert to the instruction/input/output schema expected by train_qlora.py.
    records = []
    for ex in ds:
        records.append(
            {
                "instruction": ex.get("instruction", ""),
                "input": ex.get("context", ""),
                "output": ex.get("response", ""),
            }
        )

    # Deterministic shuffle to ensure reproducible subsets across machines.
    rng = random.Random(RNG_SEED)
    indices = list(range(len(records)))
    rng.shuffle(indices)
    shuffled = [records[i] for i in indices]

    # Full set export (dolly_15k.jsonl).
    full_path = OUTPUT_DIR / "dolly_15k.jsonl"
    with full_path.open("w", encoding="utf-8") as f:
        for ex in shuffled:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"[prepare_dolly_subsets] Wrote full → {full_path} ({len(shuffled)} examples)")

    # 5k subset export: prefix of the shuffled full set.
    subset_size = 5000
    if len(shuffled) < subset_size:
        raise RuntimeError(f"Dataset too small: {len(shuffled)} < {subset_size}")

    subset_path = OUTPUT_DIR / "dolly_5k.jsonl"
    with subset_path.open("w", encoding="utf-8") as f:
        for ex in shuffled[:subset_size]:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"[prepare_dolly_subsets] Wrote 5k subset → {subset_path} ({subset_size} examples)")

    print("[prepare_dolly_subsets] Done.")


if __name__ == "__main__":
    main()
