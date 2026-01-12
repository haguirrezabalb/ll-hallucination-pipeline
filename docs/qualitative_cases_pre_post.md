# Qualitative analysis - pre vs post (seed 0)

This document summarizes the qualitative comparisons extracted from lm-eval-harness per-sample logs (`samples_*.jsonl`).

- Baseline (pre-QLoRA)
- Post-QLoRA with two representative adapters:
  - `alpaca_10k`
  - `dolly_full`

## Sources (seed 0)

Baseline (pre-QLoRA):

- TruthfulQA_mc2 samples: `evals/baseline_nf4exp/baseline_truthfulqa_mc2_seed0/__home__USER__models__qwen3-8b-base__Qwen3-8B-Base/samples_truthfulqa_mc2_2026-01-09T23-54-05.230820.jsonl`
- ARC-Easy samples: `evals/baseline_nf4exp/baseline_arc_easy_seed0/__home__USER__models__qwen3-8b-base__Qwen3-8B-Base/samples_arc_easy_2026-01-09T23-57-41.041908.jsonl`

Post-QLoRA (alpaca_10k):

- TruthfulQA_mc2 samples: `evals/postqlora_nf4exp/postqlora_truthfulqa_mc2_seed0/__home__USER__models__qwen3-8b-base-qlora-alpaca-10k/samples_truthfulqa_mc2_2026-01-10T01-15-41.464650.jsonl`
- ARC-Easy samples: `evals/postqlora_nf4exp/postqlora_arc_easy_seed0/__home__USER__models__qwen3-8b-base-qlora-alpaca-10k/samples_arc_easy_2026-01-10T01-20-34.304423.jsonl`

Post-QLoRA (dolly_full):

- TruthfulQA_mc2 samples: `evals/postqlora_nf4exp/postqlora_truthfulqa_mc2_seed0/__home__USER__models__qwen3-8b-base-qlora-dolly-full/samples_truthfulqa_mc2_2026-01-10T10-41-51.950516.jsonl`
- ARC-Easy samples: `evals/postqlora_nf4exp/postqlora_arc_easy_seed0/__home__USER__models__qwen3-8b-base-qlora-dolly-full/samples_arc_easy_2026-01-10T10-46-56.000227.jsonl`

## Post-QLoRA dumps (generated markdown)

- `alpaca_10k` combined: `docs/qualitative_cases_post_alpaca_10k_seed0.md`
- `alpaca_10k` TruthfulQA only: `docs/qualitative_cases_post_alpaca_10k_truthfulqa_seed0.md`
- `alpaca_10k` ARC-Easy only: `docs/qualitative_cases_post_alpaca_10k_arc_seed0.md`

- `dolly_full` combined: `docs/qualitative_cases_post_dolly_full_seed0.md`
- `dolly_full` TruthfulQA only: `docs/qualitative_cases_post_dolly_full_truthfulqa_seed0.md`
- `dolly_full` ARC-Easy only: `docs/qualitative_cases_post_dolly_full_arc_seed0.md`

## Interpretation notes (high level)

- TruthfulQA_mc2: `acc` is a continuous per-item MC2 score (probability mass on true options).
- ARC-Easy: `acc`/`acc_norm` are effectively binary per-item; inspect improvements/degradations in the dumps.
