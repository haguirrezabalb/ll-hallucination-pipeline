#!/usr/bin/env python3
"""
scripts/export_qlora_recipe_table.py

Purpose:
- Export a "QLoRA training recipe" table from configs/qlora_*.toml for reproducibility.

Inputs:
- configs/qlora_*.toml

Outputs:
- docs/qlora_training_recipe.csv  (full table, one row per condition)
- docs/qlora_training_recipe.md   (compact Markdown summary)

Notes:
- The recipe reflects the TOML configs exactly. If something looks wrong, fix the TOML and regenerate.
- Optional sanity checks can be enabled with --strict (dataset/output-dir mismatch detection).

Determinism / reruns:
- Output row order is deterministic (preferred order + alphabetical fallback).
"""

from __future__ import annotations

import argparse
import csv
import glob
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---
# Minimal TOML parser (project-scoped)
# ---
# Avoid adding a TOML dependency; this parser supports the subset used by configs/qlora_*.toml.
# Not a full TOML implementation (assumes simple scalars and flat lists).

def _parse_toml_value(raw: str) -> Any:
    raw = raw.strip()

    # Flat list parsing: [a, b, c]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items = [x.strip() for x in inner.split(",")]
        return [_parse_toml_value(x) for x in items]

    # Double-quoted string
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]

    # Booleans
    lower = raw.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False

    # Int
    try:
        return int(raw)
    except ValueError:
        pass

    # Float (supports scientific notation)
    try:
        return float(raw)
    except ValueError:
        pass

    # Fallback: keep as raw string
    return raw


def load_toml(path: str) -> Dict[str, Dict[str, Any]]:
    # Parse TOML into a 2-level dict: section -> {key: value}.
    cfg: Dict[str, Dict[str, Any]] = {}
    current: Optional[str] = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1].strip()
                cfg.setdefault(current, {})
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.split("#", 1)[0].strip()
                parsed = _parse_toml_value(value)

                section = current or ""
                cfg.setdefault(section, {})
                cfg[section][key] = parsed

    return cfg


def fmt(v: Any) -> str:
    # Format config values for table export (lists as comma-separated).
    if v is None:
        return ""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


# ---
# Sanity checks (project-specific)
# ---
# These checks catch common operator mistakes:
# - condition name does not match dataset_path
# - output adapter directory name does not include the expected condition token

def _normalize_condition_for_path(cond: str) -> str:
    # Convert internal condition id to a token that often appears in folder names.
    return cond.lower().replace("_", "-")


def validate_row(condition: str, dataset_path: str, lora_output_dir: str) -> List[str]:
    # Return a list of warning strings (empty if OK).
    warnings: List[str] = []
    c = (condition or "").lower()
    d = (dataset_path or "").lower()

    if c == "dolly_5k" and "dolly_5k" not in d:
        warnings.append(f"{condition}: expected dataset_path to contain 'dolly_5k' but got '{dataset_path}'")
    if c == "dolly_full" and "dolly_15k" not in d:
        warnings.append(f"{condition}: expected dataset_path to contain 'dolly_15k' but got '{dataset_path}'")
    if c.startswith("alpaca_") and "yahma/alpaca-cleaned" not in d:
        warnings.append(f"{condition}: expected dataset_path to be 'yahma/alpaca-cleaned' but got '{dataset_path}'")
    if c == "smoketest" and "smoketest" not in d:
        warnings.append(f"{condition}: expected dataset_path to contain 'smoketest' but got '{dataset_path}'")

    base = Path(lora_output_dir or "").name.lower()
    if base:
        needle = _normalize_condition_for_path(condition)
        if needle and needle not in base:
            warnings.append(
                f"{condition}: output dir basename '{base}' does not contain expected token '{needle}'"
            )

    return warnings


def main() -> None:
    p = argparse.ArgumentParser(description="Export a QLoRA training recipe table from configs/qlora_*.toml")
    p.add_argument("--glob", default="configs/qlora_*.toml", help="glob for QLoRA configs")
    p.add_argument("--out_md", default="docs/qlora_training_recipe.md", help="output Markdown path")
    p.add_argument("--out_csv", default="docs/qlora_training_recipe.csv", help="output CSV path")
    p.add_argument("--strict", action="store_true", help="fail on detected mismatches")
    args = p.parse_args()

    cfg_paths = sorted(glob.glob(args.glob))
    if not cfg_paths:
        raise SystemExit(f"No files matched: {args.glob}")

    preferred_order = ["alpaca_1k", "alpaca_10k", "alpaca_full", "dolly_5k", "dolly_full", "smoketest"]

    rows_by_condition: Dict[str, Dict[str, Any]] = {}
    fieldnames: Optional[List[str]] = None

    for cfg_path in cfg_paths:
        cfg = load_toml(cfg_path)

        model = cfg.get("model", {})
        lora = cfg.get("lora", {})
        training = cfg.get("training", {})
        seeds = cfg.get("seeds", {})
        output = cfg.get("output", {})

        condition = Path(cfg_path).stem.replace("qlora_", "")

        per_device_bs = training.get("per_device_train_batch_size", "")
        grad_accum = training.get("gradient_accumulation_steps", "")
        try:
            eff_bs = int(per_device_bs) * int(grad_accum)
        except Exception:
            eff_bs = ""

        dataset_path = fmt(training.get("dataset_path", ""))
        lora_output_dir = fmt(output.get("lora_output_dir", ""))

        warns = validate_row(condition, dataset_path, lora_output_dir)
        if warns:
            msg = "\n".join(f"[WARN] {w}" for w in warns)
            if args.strict:
                raise SystemExit(msg)
            print(msg)

        row = {
            "condition": condition,
            "config_file": Path(cfg_path).name,
            # Data
            "dataset_type": fmt(training.get("dataset_type", "")),
            "dataset_path": dataset_path,
            "max_seq_length": fmt(training.get("max_seq_length", "")),
            # Training
            "num_train_epochs": fmt(training.get("num_train_epochs", "")),
            "max_steps": fmt(training.get("max_steps", "")),
            "learning_rate": fmt(training.get("learning_rate", "")),
            "warmup_ratio": fmt(training.get("warmup_ratio", "")),
            "weight_decay": fmt(training.get("weight_decay", "")),
            "per_device_train_batch_size": fmt(per_device_bs),
            "gradient_accumulation_steps": fmt(grad_accum),
            "effective_batch_size": fmt(eff_bs),
            "max_grad_norm": fmt(training.get("max_grad_norm", "")),
            "gradient_checkpointing": fmt(training.get("gradient_checkpointing", "")),
            # Quantization (training)
            "load_in_4bit": fmt(model.get("load_in_4bit", "")),
            "quant_type": fmt(model.get("quant_type", "")),
            "compute_dtype": fmt(model.get("compute_dtype", "")),
            "use_double_quant": fmt(model.get("use_double_quant", "")),
            # LoRA
            "lora_r": fmt(lora.get("lora_r", "")),
            "lora_alpha": fmt(lora.get("lora_alpha", "")),
            "lora_dropout": fmt(lora.get("lora_dropout", "")),
            "bias": fmt(lora.get("bias", "none")),
            "target_modules": fmt(lora.get("target_modules", [])),
            # Seeds
            "train_seed": fmt(seeds.get("train_seed", "")),
            "data_seed": fmt(seeds.get("data_seed", "")),
            "model_seed": fmt(seeds.get("model_seed", "")),
            # Output
            "lora_output_dir": lora_output_dir,
        }

        if fieldnames is None:
            fieldnames = list(row.keys())

        if condition in rows_by_condition:
            raise SystemExit(f"Duplicate condition detected: {condition} (check your configs glob)")

        rows_by_condition[condition] = row

    assert fieldnames is not None

    ordered_conditions = [c for c in preferred_order if c in rows_by_condition]
    ordered_conditions += sorted(set(rows_by_condition.keys()) - set(preferred_order))
    rows: List[Dict[str, Any]] = [rows_by_condition[c] for c in ordered_conditions]

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    def md_escape(s: str) -> str:
        return str(s).replace("|", "\\|").strip()

    exclude_shared = {"condition", "config_file", "dataset_type", "dataset_path", "lora_output_dir"}
    shared: Dict[str, str] = {}
    for key in fieldnames:
        if key in exclude_shared:
            continue
        vals = [fmt(r.get(key, "")) for r in rows]
        if vals and all(v == vals[0] for v in vals):
            shared[key] = vals[0]

    md_lines: List[str] = []
    md_lines.append("# QLoRA training recipe (summary)")
    md_lines.append("")
    md_lines.append("This file is generated from `configs/qlora_*.toml`.")
    md_lines.append("For the full table (all fields), see `docs/qlora_training_recipe.csv`.")
    md_lines.append("")

    if shared:
        md_lines.append("## Shared settings (identical across all configs)")
        md_lines.append("")

        def emit(prefix: str, keys: List[str]) -> None:
            items = []
            for k in keys:
                if k in shared and shared[k] != "":
                    items.append(f"{k}={shared[k]}")
            if items:
                md_lines.append(f"- {prefix}: " + ", ".join(md_escape(x) for x in items))

        emit("quantization", ["load_in_4bit", "quant_type", "compute_dtype", "use_double_quant"])
        emit("lora", ["lora_r", "lora_alpha", "lora_dropout", "bias", "target_modules"])
        emit(
            "training",
            [
                "num_train_epochs",
                "max_steps",
                "learning_rate",
                "warmup_ratio",
                "weight_decay",
                "per_device_train_batch_size",
                "gradient_accumulation_steps",
                "effective_batch_size",
                "max_grad_norm",
                "gradient_checkpointing",
            ],
        )
        emit("seeds", ["train_seed", "data_seed", "model_seed"])
        md_lines.append("")

    md_lines.append("## Per-condition settings")
    md_lines.append("")
    md_lines.append(
        "Note: `lora_output_dir` is shown as the adapter folder name (basename). "
        "Full paths are in `docs/qlora_training_recipe.csv`."
    )
    md_lines.append("")

    md_headers = ["condition", "dataset_type", "dataset_path", "max_seq_length", "adapter_dir"]
    md_lines.append("| " + " | ".join(md_headers) + " |")
    md_lines.append("| " + " | ".join(["---"] * len(md_headers)) + " |")

    for r in rows:
        adapter_dir = Path(fmt(r.get("lora_output_dir", ""))).name
        cells = [
            fmt(r.get("condition", "")),
            fmt(r.get("dataset_type", "")),
            fmt(r.get("dataset_path", "")),
            fmt(r.get("max_seq_length", "")),
            adapter_dir,
        ]
        md_lines.append("| " + " | ".join(md_escape(x) for x in cells) + " |")

    md_lines.append("")
    out_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[OK] Wrote CSV: {out_csv}")
    print(f"[OK] Wrote MD : {out_md}")


if __name__ == "__main__":
    main()
