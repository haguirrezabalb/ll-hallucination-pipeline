#!/usr/bin/env python3
"""
Generate qualitative ARC-Easy pre vs post comparisons (baseline vs one adapter), for a given seed.

Purpose:
- Produce a deterministic Markdown report with ARC-Easy improvements/degradations (pre vs post).

Inputs (latest by mtime):
- Baseline: evals/baseline/baseline_arc_easy_seed{seed}/**/samples_arc_easy_*.jsonl
- Post:     evals/postqlora/by_adapter/{adapter}/arc_easy_seed{seed}/samples_arc_easy_*.jsonl

Output:
- docs/qualitative_arc_pre_vs_{adapter}_seed{seed}.md

Notes / conventions:
- Correct/incorrect is computed w.r.t. the unnormalized argmax over filtered_resps,
  which aligns with lm-eval's `acc` convention for ARC tasks (binary correctness).
- acc_norm is reported as-is from the JSONL for context and may disagree with acc.

Determinism / reruns:
- We always select the newest samples file by mtime to be rerun-safe.
- We select the first K improvements/degradations by doc_id order.
"""

from __future__ import annotations

import argparse
import json
import re
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


def extract_choices(doc: Dict[str, Any]) -> List[Tuple[str, str]]:
    # Returns [(label, text), ...] for ARC-style multiple-choice.
    choices = doc.get("choices")
    if isinstance(choices, dict):
        labels = choices.get("label") or choices.get("labels")
        texts = choices.get("text") or choices.get("texts")
        if isinstance(labels, list) and isinstance(texts, list) and len(labels) == len(texts):
            return [(str(l), str(t)) for l, t in zip(labels, texts)]

    q = doc.get("question")
    if isinstance(q, dict):
        choices2 = q.get("choices")
        if isinstance(choices2, dict):
            labels = choices2.get("label") or choices2.get("labels")
            texts = choices2.get("text") or choices2.get("texts")
            if isinstance(labels, list) and isinstance(texts, list) and len(labels) == len(texts):
                return [(str(l), str(t)) for l, t in zip(labels, texts)]
        if isinstance(choices2, list):
            out: List[Tuple[str, str]] = []
            for i, item in enumerate(choices2):
                if isinstance(item, dict):
                    lab = item.get("label", None) or item.get("key", None) or chr(ord("A") + i)
                    txt = item.get("text", None) or item.get("value", None) or ""
                    out.append((str(lab), str(txt)))
            if out:
                return out

    opts = doc.get("options") or doc.get("answers") or None
    if isinstance(opts, list) and opts:
        out = []
        for i, t in enumerate(opts):
            out.append((chr(ord("A") + i), str(t)))
        return out

    return []


def correct_idx_from_doc(doc: Dict[str, Any], labels: List[str]) -> int:
    # Resolve correct index from ARC-style answerKey (supports A-D and 1-4).
    ans = doc.get("answerKey") or doc.get("answer") or doc.get("gold")
    if isinstance(ans, dict):
        ans = ans.get("answerKey") or ans.get("answer")
    if ans is None:
        return -1

    s = str(ans).strip()

    if labels:
        for i, lab in enumerate(labels):
            if str(lab).strip() == s:
                return i

    if len(s) == 1 and s.upper() in ["A", "B", "C", "D"]:
        return ord(s.upper()) - ord("A")

    if re.fullmatch(r"[1-4]", s):
        return int(s) - 1

    return -1


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate qualitative ARC-Easy pre vs post comparisons (baseline vs adapter).")
    ap.add_argument("--adapter", required=True, help="Adapter name (e.g., alpaca_10k, dolly_full)")
    ap.add_argument("--seed", type=int, default=0, help="Seed (default: 0)")
    ap.add_argument("--limit", type=int, default=10, help="Top-k to show for improvements and degradations (default: 10)")
    ap.add_argument("--out", default=None, help="Output path (default: docs/qualitative_arc_pre_vs_{adapter}_seed{seed}.md)")
    args = ap.parse_args()

    adapter = args.adapter.strip()
    seed = args.seed
    limit = args.limit

    project_root = Path(__file__).resolve().parents[1]
    docs_dir = project_root / "docs"

    baseline_samples = newest_file(
        f"evals/baseline/baseline_arc_easy_seed{seed}/**/samples_arc_easy_*.jsonl",
        project_root,
    )
    post_samples = newest_file(
        f"evals/postqlora/by_adapter/{adapter}/arc_easy_seed{seed}/samples_arc_easy_*.jsonl",
        project_root,
    )

    pre = load_jsonl_map(baseline_samples)
    post = load_jsonl_map(post_samples)
    common = sorted(set(pre.keys()) & set(post.keys()))

    improvements: List[int] = []
    degradations: List[int] = []
    cases: Dict[int, Dict[str, Any]] = {}

    for did in common:
        a = pre[did]
        b = post[did]

        acc_pre = get_metric(a, "acc") or 0.0
        accn_pre = get_metric(a, "acc_norm") or 0.0
        acc_post = get_metric(b, "acc") or 0.0
        accn_post = get_metric(b, "acc_norm") or 0.0

        doc_a = a.get("doc", {}) if isinstance(a.get("doc", {}), dict) else {}
        doc_b = b.get("doc", {}) if isinstance(b.get("doc", {}), dict) else {}
        doc = doc_a or doc_b

        choices = extract_choices(doc)
        labels = [lab for lab, _ in choices]

        correct_idx = correct_idx_from_doc(doc, labels)
        pred_pre = argmax_idx_from_filtered_resps(a)
        pred_post = argmax_idx_from_filtered_resps(b)

        is_correct_pre = bool(round(acc_pre)) if pred_pre < 0 or correct_idx < 0 else (pred_pre == correct_idx)
        is_correct_post = bool(round(acc_post)) if pred_post < 0 or correct_idx < 0 else (pred_post == correct_idx)

        q = doc.get("question")
        if isinstance(q, dict):
            q_text = q.get("stem") or q.get("question") or ""
        else:
            q_text = q or ""
        q_text = str(q_text).strip()

        cases[did] = dict(
            did=did,
            question=q_text,
            choices=choices,
            correct_idx=correct_idx,
            pred_pre=pred_pre,
            pred_post=pred_post,
            acc_pre=int(round(acc_pre)),
            accn_pre=int(round(accn_pre)),
            acc_post=int(round(acc_post)),
            accn_post=int(round(accn_post)),
            is_correct_pre=is_correct_pre,
            is_correct_post=is_correct_post,
        )

        if (not is_correct_pre) and is_correct_post:
            improvements.append(did)
        if is_correct_pre and (not is_correct_post):
            degradations.append(did)

    improvements = sorted(improvements)[:limit]
    degradations = sorted(degradations)[:limit]

    out_path = Path(args.out) if args.out else (docs_dir / f"qualitative_arc_pre_vs_{adapter}_seed{seed}.md")

    rel_pre = anonymize_model_dir(baseline_samples.relative_to(project_root).as_posix())
    rel_post = anonymize_model_dir(post_samples.relative_to(project_root).as_posix())


    lines: List[str] = []
    lines.append(f"# Qualitative cases - ARC-Easy (seed{seed}) - baseline vs {adapter}\n\n")
    lines.append(f"- Baseline samples: `{rel_pre}`\n\n")
    lines.append(f"- Post ({adapter}) samples: `{rel_post}`\n\n")
    lines.append("Selection criterion:\n")
    lines.append("\n- Correct/incorrect is based on `acc` (unnormalized loglikelihood argmax over choices).\n")
    lines.append("- `acc_norm` is reported for context and may disagree with `acc`.\n\n")

    lines.append(f"## Improvements (PRE incorrect → POST correct), top {len(improvements)}\n\n")
    for did in improvements:
        c = cases[did]
        lines.append(f"### doc_id={did}\n\n")
        lines.append(f"Q: {md_escape(c['question'])}\n\n")
        lines.append(f"**PRE**: acc={c['acc_pre']} | acc_norm={c['accn_pre']} | pred_idx={c['pred_pre']} | correct_idx={c['correct_idx']} | is_correct={c['is_correct_pre']}\n\n")
        for i, (lab, txt) in enumerate(c["choices"]):
            tags = []
            if i == c["pred_pre"]:
                tags.append("PRED")
            if i == c["correct_idx"]:
                tags.append("GT")
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- [{lab}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")
        lines.append(f"**POST**: acc={c['acc_post']} | acc_norm={c['accn_post']} | pred_idx={c['pred_post']} | correct_idx={c['correct_idx']} | is_correct={c['is_correct_post']}\n\n")
        for i, (lab, txt) in enumerate(c["choices"]):
            tags = []
            if i == c["pred_post"]:
                tags.append("PRED")
            if i == c["correct_idx"]:
                tags.append("GT")
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- [{lab}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")

    lines.append(f"## Degradations (PRE correct → POST incorrect), top {len(degradations)}\n\n")
    for did in degradations:
        c = cases[did]
        lines.append(f"### doc_id={did}\n\n")
        lines.append(f"Q: {md_escape(c['question'])}\n\n")
        lines.append(f"**PRE**: acc={c['acc_pre']} | acc_norm={c['accn_pre']} | pred_idx={c['pred_pre']} | correct_idx={c['correct_idx']} | is_correct={c['is_correct_pre']}\n\n")
        for i, (lab, txt) in enumerate(c["choices"]):
            tags = []
            if i == c["pred_pre"]:
                tags.append("PRED")
            if i == c["correct_idx"]:
                tags.append("GT")
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- [{lab}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")
        lines.append(f"**POST**: acc={c['acc_post']} | acc_norm={c['accn_post']} | pred_idx={c['pred_post']} | correct_idx={c['correct_idx']} | is_correct={c['is_correct_post']}\n\n")
        for i, (lab, txt) in enumerate(c["choices"]):
            tags = []
            if i == c["pred_post"]:
                tags.append("PRED")
            if i == c["correct_idx"]:
                tags.append("GT")
            tag_str = f"  [{' ,'.join(tags)}]" if tags else ""
            lines.append(f"- [{lab}] {md_escape(txt)}{tag_str}\n")
        lines.append("\n")

    raw = "".join(lines)
    out_path.write_text(collapse_blank_lines(raw), encoding="utf-8")
    print(f"[generate_qualitative_arc_pre_vs_post] Wrote: {out_path}")


if __name__ == "__main__":
    main()
