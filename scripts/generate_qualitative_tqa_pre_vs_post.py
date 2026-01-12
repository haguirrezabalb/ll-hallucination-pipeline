#!/usr/bin/env python3
"""
Generate qualitative TruthfulQA_mc2 pre vs post comparisons (baseline vs one adapter), for a given seed.

Purpose:
- Produce a deterministic Markdown report with TruthfulQA_mc2 improvements/degradations (pre vs post).

Inputs (latest by mtime):
- Baseline: evals/baseline/baseline_truthfulqa_mc2_seed{seed}/**/samples_truthfulqa_mc2_*.jsonl
- Post:     evals/postqlora/by_adapter/{adapter}/truthfulqa_mc2_seed{seed}/samples_truthfulqa_mc2_*.jsonl

Output:
- docs/qualitative_tqa_pre_vs_{adapter}_seed{seed}.md

Notes / conventions:
- acc is the per-item MC2 score (probability mass on true options), continuous in [0, 1].
- Improvements/degradations are defined by argmax switching (F→T or T→F), not by delta_acc alone.

Determinism / reruns:
- We always select the newest samples file by mtime to be rerun-safe.
- We select top-K by delta_acc within each category.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Helpers

def newest_file(glob_pattern: str, root: Path) -> Path:
    # Select newest file by mtime to be robust to reruns (multiple samples_*.jsonl).
    matches = list(root.glob(glob_pattern))
    if not matches:
        raise FileNotFoundError(f"No matches for pattern: {glob_pattern}")
    matches.sort(key=lambda p: p.stat().st_mtime)
    return matches[-1]


def anonymize_model_dir(p: str) -> str:
    # Anonymize lm-eval sanitized home directory component for portability.
    user = os.environ.get("USER", "USER")
    return p.replace(f"__home__{user}__", "__home__USER__")


def load_jsonl_map(path: Path) -> Dict[int, Dict[str, Any]]:
    # Load lm-eval JSONL samples into a {doc_id -> sample} map for easy alignment.
    out: Dict[int, Dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            did = obj.get("doc_id", None)
            if did is None:
                did = obj.get("id", None) or obj.get("doc", {}).get("doc_id", None)
            if did is None:
                continue
            out[int(did)] = obj
    return out


def try_float(x: Any) -> Optional[float]:
    # Best-effort float parsing (returns None if conversion fails).
    try:
        return float(x)
    except Exception:
        return None


def get_metric(sample: Dict[str, Any], name: str) -> Optional[float]:
    # Metrics can be stored at top-level or inside sample["metrics"] depending on lm-eval version.
    if name in sample:
        return try_float(sample.get(name))
    m = sample.get("metrics")
    if isinstance(m, dict) and name in m:
        return try_float(m.get(name))
    return None


def argmax_idx_from_filtered_resps(sample: Dict[str, Any]) -> int:
    # Compute argmax index over lm-eval filtered_resps scores (first element per choice).
    fr = sample.get("filtered_resps", None)
    if not isinstance(fr, list) or not fr:
        return -1
    scores: List[float] = []
    for r in fr:
        if isinstance(r, (list, tuple)) and r:
            s = try_float(r[0])
            scores.append(s if s is not None else float("-inf"))
        else:
            scores.append(float("-inf"))
    if not scores:
        return -1
    return max(range(len(scores)), key=lambda i: scores[i])


def md_escape(s: str) -> str:
    # Escape MD table separators and trim whitespace.
    return str(s).replace("|", "\\|").strip()


def collapse_blank_lines(text: str) -> str:
    out = []
    blank = False
    for line in text.splitlines():
        if line.strip() == "":
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(line)
    return "\n".join(out).rstrip() + "\n"



def extract_mc2(doc: Dict[str, Any]) -> Tuple[str, List[str], List[int]]:
    # Return (question, choices, labels) for TruthfulQA_mc2.
    # labels: 1 for true, 0 for false (per choice).
    q = str(doc.get("question", "")).strip()

    mc2 = doc.get("mc2_targets", {})
    choices = mc2.get("choices", []) if isinstance(mc2, dict) else []
    labels = mc2.get("labels", []) if isinstance(mc2, dict) else []

    choices_s = [str(c) for c in choices] if isinstance(choices, list) else []
    labels_i = [int(x) for x in labels] if isinstance(labels, list) else []
    return q, choices_s, labels_i


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate qualitative TruthfulQA_mc2 pre vs post comparisons (baseline vs adapter).")
    ap.add_argument("--adapter", required=True, help="Adapter name (e.g., alpaca_10k, dolly_full)")
    ap.add_argument("--seed", type=int, default=0, help="Seed (default: 0)")
    ap.add_argument("--limit", type=int, default=10, help="Top-k to show for improvements and degradations (default: 10)")
    ap.add_argument("--out", default=None, help="Output path (default: docs/qualitative_tqa_pre_vs_{adapter}_seed{seed}.md)")
    args = ap.parse_args()

    adapter = args.adapter.strip()
    seed = args.seed
    limit = args.limit

    project_root = Path(__file__).resolve().parents[1]
    docs_dir = project_root / "docs"
    task = "truthfulqa_mc2"

    baseline_samples = newest_file(
        f"evals/baseline/baseline_{task}_seed{seed}/**/samples_{task}_*.jsonl",
        project_root,
    )
    post_samples = newest_file(
        f"evals/postqlora/by_adapter/{adapter}/{task}_seed{seed}/samples_{task}_*.jsonl",
        project_root,
    )

    pre = load_jsonl_map(baseline_samples)
    post = load_jsonl_map(post_samples)
    common = sorted(set(pre.keys()) & set(post.keys()))

    rows: List[Dict[str, Any]] = []
    for did in common:
        a = pre[did]
        b = post[did]

        acc_pre = float(get_metric(a, "acc") or 0.0)
        acc_post = float(get_metric(b, "acc") or 0.0)
        dacc = acc_post - acc_pre

        pre_idx = argmax_idx_from_filtered_resps(a)
        post_idx = argmax_idx_from_filtered_resps(b)

        doc = a.get("doc", {}) if isinstance(a.get("doc", {}), dict) else {}
        if not doc:
            doc = b.get("doc", {}) if isinstance(b.get("doc", {}), dict) else {}

        q, choices, labels = extract_mc2(doc)

        def is_true(idx: int) -> bool:
            if idx < 0 or idx >= len(labels):
                return False
            return int(labels[idx]) == 1

        pre_tf = "T" if is_true(pre_idx) else "F"
        post_tf = "T" if is_true(post_idx) else "F"

        rows.append(
            dict(
                doc_id=did,
                acc_pre=acc_pre,
                acc_post=acc_post,
                delta_acc=dacc,
                pre_idx=pre_idx,
                post_idx=post_idx,
                pre_tf=pre_tf,
                post_tf=post_tf,
                question=q,
                choices=choices,
                labels=labels,
            )
        )

    improvements = [r for r in rows if r["pre_tf"] == "F" and r["post_tf"] == "T"]
    degradations = [r for r in rows if r["pre_tf"] == "T" and r["post_tf"] == "F"]

    improvements.sort(key=lambda r: r["delta_acc"], reverse=True)
    degradations.sort(key=lambda r: r["delta_acc"])

    improvements = improvements[:limit]
    degradations = degradations[:limit]

    out_path = Path(args.out) if args.out else (docs_dir / f"qualitative_tqa_pre_vs_{adapter}_seed{seed}.md")

    rel_pre = anonymize_model_dir(baseline_samples.relative_to(project_root).as_posix())
    rel_post = anonymize_model_dir(post_samples.relative_to(project_root).as_posix())


    lines: List[str] = []
    lines.append(f"# Qualitative cases - TruthfulQA_mc2 (seed{seed}) - baseline vs {adapter}\n\n")
    lines.append(f"- Baseline samples: `{rel_pre}`\n\n")
    lines.append(f"- Post ({adapter}) samples: `{rel_post}`\n\n")
    lines.append("Selection criterion:\n")
    lines.append("\n- Improvements: argmax switches from a false option (PRE) to a true option (POST).\n")
    lines.append("- Degradations: argmax switches from a true option (PRE) to a false option (POST).\n")
    lines.append("- Sorted by Δacc = acc_post − acc_pre.\n\n")

    def render_case(r: Dict[str, Any]) -> None:
        did = r["doc_id"]
        lines.append(f"### doc_id={did}\n\n")
        lines.append(f"Q: {md_escape(r['question'])}\n\n")
        lines.append(f"**PRE**: acc={r['acc_pre']:.6f} | pred_idx={r['pre_idx']} ({r['pre_tf']})\n\n")
        for i, (txt, lab) in enumerate(zip(r["choices"], r["labels"])):
            tags = []
            if i == r["pre_idx"]:
                tags.append("PRED")
            tf = "T" if int(lab) == 1 else "F"
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- ({tf}) [{i}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")
        lines.append(f"**POST**: acc={r['acc_post']:.6f} | pred_idx={r['post_idx']} ({r['post_tf']}) | Δacc={r['delta_acc']:+.6f}\n\n")
        for i, (txt, lab) in enumerate(zip(r["choices"], r["labels"])):
            tags = []
            if i == r["post_idx"]:
                tags.append("PRED")
            tf = "T" if int(lab) == 1 else "F"
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- ({tf}) [{i}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")

    lines.append(f"## Improvements (PRE argmax F → POST argmax T), top {len(improvements)}\n\n")
    for r in improvements:
        render_case(r)

    lines.append(f"## Degradations (PRE argmax T → POST argmax F), top {len(degradations)}\n\n")
    for r in degradations:
        render_case(r)

    raw = "".join(lines)
    out_path.write_text(collapse_blank_lines(raw), encoding="utf-8")
    print(f"[generate_qualitative_tqa_pre_vs_post] Wrote: {out_path}")


if __name__ == "__main__":
    main()
