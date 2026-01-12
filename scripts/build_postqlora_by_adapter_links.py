#!/usr/bin/env python3
"""
scripts/build_postqlora_by_adapter_links.py

Purpose:
- Build and validate the evals/postqlora/by_adapter symlink tree from lm-eval-harness outputs.

Inputs:
- evals/postqlora/postqlora_<task>_seed<seed>/  (lm-eval output folders)

Outputs:
- evals/postqlora/by_adapter/<adapter>/<task>_seed<seed> -> <model_dir>
  where <model_dir> is the lm-eval subdirectory that encodes the model+adapter path.

Notes:
- Non-destructive: if a symlink exists and points to the expected target, it is kept.
- Validates that each linked target contains at least one results_*.json and one samples_*.jsonl.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Optional, Tuple


RUN_DIR_RE = re.compile(r"^postqlora_(?P<task>.+)_seed(?P<seed>\d+)$")
DEFAULT_MODEL_MARKER = "qwen3-8b-base-qlora-"


def parse_run_dir_name(name: str) -> Optional[Tuple[str, int]]:
    match = RUN_DIR_RE.match(name)
    if not match:
        return None
    task = match.group("task")
    seed = int(match.group("seed"))
    return task, seed


def adapter_id_from_model_dir(dir_name: str, model_marker: str) -> Optional[str]:
    idx = dir_name.find(model_marker)
    if idx == -1:
        return None

    adapter_suffix = dir_name[idx + len(model_marker) :].strip()
    if not adapter_suffix:
        return None

    # Canonicalize: "alpaca-10k" -> "alpaca_10k"
    return adapter_suffix.replace("-", "_")


def count_artifacts(model_dir: Path) -> Tuple[int, int]:
    results_count = len(list(model_dir.glob("results_*.json")))
    samples_count = len(list(model_dir.glob("samples_*.jsonl")))
    return results_count, samples_count


def ensure_symlink(link_path: Path, target_dir: Path, dry_run: bool) -> str:
    """
    Returns one of:
      - "created"
      - "exists_ok"
      - "exists_mismatch"
      - "exists_not_symlink"
    """
    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink():
            try:
                current_target = link_path.resolve()
            except FileNotFoundError:
                current_target = None

            if current_target is not None and current_target == target_dir.resolve():
                return "exists_ok"
            return "exists_mismatch"

        return "exists_not_symlink"

    rel_target = os.path.relpath(target_dir, start=link_path.parent)
    if not dry_run:
        link_path.symlink_to(rel_target, target_is_directory=True)
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate evals/postqlora/by_adapter symlinks from postqlora_*_seed* runs."
    )
    parser.add_argument(
        "--base-dir",
        default="evals/postqlora",
        help="Directory containing postqlora_<task>_seed<seed> folders.",
    )
    parser.add_argument(
        "--out-dir",
        default="evals/postqlora/by_adapter",
        help="Output directory for by-adapter symlinks.",
    )
    parser.add_argument(
        "--model-marker",
        default=DEFAULT_MODEL_MARKER,
        help="Substring used to extract the adapter suffix from lm-eval model directory names.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not create symlinks; only report what would be done.",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not base_dir.exists():
        print(f"ERROR: base-dir does not exist: {base_dir}")
        return 2

    run_dirs = []
    for child in sorted(base_dir.iterdir()):
        if not child.is_dir():
            continue
        if parse_run_dir_name(child.name) is None:
            continue
        run_dirs.append(child)

    if not run_dirs:
        print(f"ERROR: no postqlora_<task>_seed<seed> run directories found under: {base_dir}")
        return 2

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    exists_ok = 0
    exists_mismatch = 0
    exists_not_symlink = 0
    skipped_no_marker = 0
    skipped_missing_artifacts = 0
    checks_ok = 0
    checks_bad = 0

    for run_dir in run_dirs:
        parsed = parse_run_dir_name(run_dir.name)
        if parsed is None:
            continue
        task, seed = parsed

        for model_dir in sorted([p for p in run_dir.iterdir() if p.is_dir()]):
            adapter_id = adapter_id_from_model_dir(model_dir.name, args.model_marker)
            if adapter_id is None:
                skipped_no_marker += 1
                continue

            r_cnt, s_cnt = count_artifacts(model_dir)
            if r_cnt < 1 or s_cnt < 1:
                skipped_missing_artifacts += 1
                continue

            adapter_dir = out_dir / adapter_id
            link_path = adapter_dir / f"{task}_seed{seed}"

            if not args.dry_run:
                adapter_dir.mkdir(parents=True, exist_ok=True)

            status = ensure_symlink(link_path, model_dir, args.dry_run)
            if status == "created":
                created += 1
            elif status == "exists_ok":
                exists_ok += 1
            elif status == "exists_mismatch":
                exists_mismatch += 1
            elif status == "exists_not_symlink":
                exists_not_symlink += 1

            check_dir = link_path if (link_path.exists() or link_path.is_symlink()) else model_dir
            r2_cnt, s2_cnt = count_artifacts(check_dir)

            if r2_cnt >= 1 and s2_cnt >= 1:
                checks_ok += 1
                print(f"OK  {link_path}  (results={r2_cnt} samples={s2_cnt})")
            else:
                checks_bad += 1
                print(f"BAD {link_path}  (results={r2_cnt} samples={s2_cnt})")

    print("")
    print("Summary")
    print(f"- base_dir                 : {base_dir}")
    print(f"- out_dir                  : {out_dir}")
    print(f"- dry_run                  : {args.dry_run}")
    print(f"- symlinks created         : {created}")
    print(f"- symlinks already OK      : {exists_ok}")
    print(f"- symlinks mismatched      : {exists_mismatch}")
    print(f"- paths not symlinks       : {exists_not_symlink}")
    print(f"- skipped (no marker)      : {skipped_no_marker}")
    print(f"- skipped (missing files)  : {skipped_missing_artifacts}")
    print(f"- checks OK                : {checks_ok}")
    print(f"- checks BAD               : {checks_bad}")

    if checks_bad > 0 or exists_mismatch > 0 or exists_not_symlink > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
