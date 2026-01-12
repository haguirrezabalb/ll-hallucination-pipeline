# ll-hallucination-pipeline

Bachelor's Thesis (BSc in Computer Engineering) — Mitigating hallucinations in LLMs via efficient SFT with QLoRA.

This repository implements a reproducible pre/post evaluation pipeline to measure how parameter-efficient supervised fine-tuning (SFT) with QLoRA affects:

- **Factual truthfulness** (as a proxy for hallucination)
- **General utility** on a standard reasoning benchmark

Backbone model (kept fixed):

- Qwen3-8B-Base (local checkpoint), evaluated under a frozen, quantized runtime protocol (4-bit NF4).

The core methodological rule is to keep the evaluation protocol frozen so any observed changes can be attributed to the LoRA adapters, not to evaluation drift.

## What this project measures

### Benchmarks (lm-eval-harness)

- **TruthfulQA_mc2**: factual truthfulness proxy (adversarial multiple choice).
- **ARC-Easy**: general utility proxy (multiple choice science questions).

### Metrics

- **TruthfulQA_mc2**
  - `acc` is the MC2 score: probability mass assigned to the set of true options.
  - Hallucination proxy (HR) is defined as: `HR = 1 - acc`
  - Interpretation: lower HR means more mass on true options (higher truthfulness).

- **ARC-Easy**
  - `acc`: standard accuracy (argmax by log-likelihood).
  - `acc_norm`: length-normalized accuracy (reduces option-length bias).
  - Utility is operationalized primarily as: `U = acc_norm`

### Statistical analysis

- Bootstrap confidence intervals (CIs) from per-sample logs (`samples_*.jsonl`).
- Paired testing on ARC-Easy using the exact McNemar test (item-level pre vs post).

## Frozen evaluation policy (reproducibility contract)

The evaluation protocol must be identical pre and post QLoRA.

Fixed settings:

- Seeds: `{0, 1, 2}`
- `num_fewshot = 0` (zero-shot)
- Multiple-choice evaluation by log-likelihood scoring (no free-form generation)
- Batching: `batch_size=auto`, `max_batch_size=4`
- Quantization (runtime, bitsandbytes): 4-bit NF4 + double quant, compute dtype bfloat16
- Prompts: default task templates from lm-eval-harness (no ad hoc prompt engineering)

The frozen policy is stored in:

- `configs/inference.toml`

## Where to find results (source of truth)

- Baseline (pre-adapter): `docs/eval_card_pre.md`
- Post-QLoRA (multi-adapter): `docs/eval_card_post.md`
- Aggregated metrics and pre/post deltas: `evals/**` (see `evals/README.md`)

Note: To avoid documentation drift, this README does not hardcode a numeric results snapshot. Use the evaluation cards and CSV artifacts as the source of truth.

## How to reproduce the pipeline

See the step-by-step runbook:

- `docs/runbook.md`

## Repository layout (high level)

- `configs/` — inference and QLoRA training configs (`*.toml`)
- `scripts/` — pipeline entrypoints (train, eval, summarize, stats, exports)
- `evals/` — lm-eval-harness outputs and derived CSV/statistics (often regenerable)
- `docs/` — evaluation cards and generated reports/figures

## License

See the thesis and institutional constraints. The backbone checkpoint and datasets have their own licenses and must be used accordingly.
