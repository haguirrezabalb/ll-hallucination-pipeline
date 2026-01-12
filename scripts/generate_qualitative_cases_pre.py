#!/usr/bin/env python3
"""
Generate qualitative case dumps for the baseline (pre-QLoRA).

Purpose:
- Build Markdown dumps from lm-eval per-sample logs for baseline seed folders.
- Reuse existing inspector scripts (TruthfulQA + ARC) and capture their output.

Inputs (latest by mtime):
- TruthfulQA: evals/baseline/baseline_truthfulqa_mc2_seed{seed}/**/samples_truthfulqa_mc2_*.jsonl
- ARC-Easy:   evals/baseline/baseline_arc_easy_seed{seed}/**/samples_arc_easy_*.jsonl

Outputs:
- docs/qualitative_cases_pre_truthfulqa.md
- docs/qualitative_cases_pre_arc.md
- docs/qualitative_cases_pre.md  (combined)

Notes / conventions:
- TruthfulQA inspector: scripts/inspect_truthfulqa_pre.py
- ARC inspector: scripts/inspect_arc_pre.py

Determinism / reruns:
- Selected always the newest samples file by mtime to be rerun-safe.
"""

from __future__ import annotations

import argparse
import re
import os
import subprocess
import sys
from pathlib import Path

# Inspectors print long "=" separator between examples.
# Normalized into MD horizontal rules for clean rendering.
SEP_RE = re.compile(r"^\={5,}\s*$")


def newest_file(glob_pattern: str, root: Path) -> Path:
    # Select newest file by mtime (robust to reruns) (multiple samples_*.jsonl).
    matches = list(root.glob(glob_pattern))
    if not matches:
        raise FileNotFoundError(f"No matches for pattern: {glob_pattern}")
    matches.sort(key=lambda p: p.stat().st_mtime)
    return matches[-1]

def anonymize_model_dir(p: str) -> str:
    # Anonymize lm-eval sanitized home directory component for portability.
    user = os.environ.get("USER", "USER")
    return p.replace(f"__home__{user}__", "__home__USER__")


def sanitize_inspector_output(text: str) -> str:
    # Convert inspector separators into MD-friendly formatting.
    out_lines: list[str] = []
    for line in text.splitlines():
        if SEP_RE.match(line.strip()):
            out_lines.append("---")
        else:
            out_lines.append(line.rstrip())

    # Collapse repeated horizontal rules.
    collapsed: list[str] = []
    prev = None
    for line in out_lines:
        if line == "---" and prev == "---":
            continue
        collapsed.append(line)
        prev = line

    # Ensure stable trailing newline for clean diffs.
    return "\n".join(collapsed).strip() + "\n"


def run_capture(cmd: list[str]) -> str:
    # Run a command and capture combined stdout/stderr.
    # check=True fails fast if an inspector crashes.
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=True,
    )
    return res.stdout


def write_md(path: Path, title: str, generated_from: list[str], body: str) -> None:
    # Write a small Markdown document with a title, provenance, and the inspector body.
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# {title}\n\n")
    lines.append("Generated from:\n")
    for p in generated_from:
        lines.append(f"\n- {p}\n")
    lines.append("\n")
    lines.append(body)
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate qualitative case dumps for baseline (pre-QLoRA).")
    ap.add_argument("--seed", type=int, default=0, help="Seed folder to use (default: 0)")

    # Baseline defaults are intentionally stricter (smaller dumps) to keep artifact short.
    ap.add_argument("--tqa_limit", type=int, default=5, help="Max TruthfulQA cases to print")
    ap.add_argument("--tqa_max_acc", type=float, default=0.05, help="TruthfulQA filter: acc <= max_acc")
    ap.add_argument("--arc_limit", type=int, default=5, help="Max ARC cases to print")

    ap.add_argument("--arc_only_incorrect", action="store_true", help="Only show incorrect ARC cases")
    args = ap.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    docs_dir = project_root / "docs"

    # Locate newest baseline sample files for the chosen seed (mtime-based, rerun-safe).
    tqa_samples = newest_file(
        f"evals/baseline/baseline_truthfulqa_mc2_seed{args.seed}/**/samples_truthfulqa_mc2_*.jsonl",
        project_root,
    )
    arc_samples = newest_file(
        f"evals/baseline/baseline_arc_easy_seed{args.seed}/**/samples_arc_easy_*.jsonl",
        project_root,
    )

    # Use portable relative paths in MD.
    tqa_rel = anonymize_model_dir(tqa_samples.relative_to(project_root).as_posix())
    arc_rel = anonymize_model_dir(arc_samples.relative_to(project_root).as_posix())

    out_tqa = docs_dir / "qualitative_cases_pre_truthfulqa.md"
    out_arc = docs_dir / "qualitative_cases_pre_arc.md"
    out_combined = docs_dir / "qualitative_cases_pre.md"

    # TruthfulQA (baseline)
    cmd_tqa = [
        sys.executable,
        str(project_root / "scripts" / "inspect_truthfulqa_pre.py"),
        "--samples",
        str(tqa_samples),
        "--limit",
        str(args.tqa_limit),
        "--max_acc",
        str(args.tqa_max_acc),
    ]
    tqa_body = sanitize_inspector_output(run_capture(cmd_tqa))

    # ARC (baseline)
    cmd_arc = [
        sys.executable,
        str(project_root / "scripts" / "inspect_arc_pre.py"),
        "--samples",
        str(arc_samples),
        "--limit",
        str(args.arc_limit),
    ]
    if args.arc_only_incorrect:
        cmd_arc.append("--only_incorrect")
    arc_body = sanitize_inspector_output(run_capture(cmd_arc))

    # Per-task MD files
    write_md(
        out_tqa,
        title=f"Qualitative cases - baseline (pre-QLoRA) - TruthfulQA_mc2 (seed {args.seed})",
        generated_from=[tqa_rel],
        body=tqa_body,
    )
    write_md(
        out_arc,
        title=f"Qualitative cases - baseline (pre-QLoRA) - ARC-Easy (seed {args.seed})",
        generated_from=[arc_rel],
        body=arc_body,
    )

    # Combined canonical file
    combined: list[str] = []
    combined.append("# Qualitative cases - baseline (pre-QLoRA)\n\n")
    combined.append("Generated from:\n")
    combined.append(f"\n- {tqa_rel}\n")
    combined.append(f"- {arc_rel}\n\n")
    combined.append("## TruthfulQA_mc2\n\n")
    combined.append(tqa_body)
    combined.append("\n---\n\n## ARC-Easy\n\n")
    combined.append(arc_body)
    out_combined.write_text("".join(combined), encoding="utf-8")

    print("[generate_qualitative_cases_pre] Wrote:")
    print(f"  - {out_tqa}")
    print(f"  - {out_arc}")
    print(f"  - {out_combined}")


if __name__ == "__main__":
    main()
