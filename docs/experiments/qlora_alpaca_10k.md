# QLoRA Experiment - Alpaca 10K

- Date (training run): 2025-12-07
- Repository commit: `<555b2b8>`
- Base model: Qwen3-8B-Base
- LoRA adapter output dir: `~/models/qwen3-8b-base-qlora-alpaca-10k`
- Training config: `configs/qlora_alpaca_10k.toml`
- Inference config (pre/post comparable): `configs/inference.toml`

## SFT training setup

- SFT dataset: `yahma/alpaca-cleaned`
- max_train_samples: 10,000
- max_seq_length: 1024
- Epochs: 3 (max_steps = -1)
- Effective batch size: 1 × 16 = 16
- Learning rate: 2e-4 (warmup_ratio = 0.03, weight_decay = 0.0)
- Gradient checkpointing: true (max_grad_norm = 0.3)

## QLoRA / LoRA settings

- Quantization (training): 4-bit NF4, compute_dtype = bfloat16, use_double_quant = true
- Rank (r): 64
- lora_alpha: 16
- lora_dropout: 0.05
- target_modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

## Evaluation protocol

- Harness: lm-eval-harness
- Tasks (0-shot): TruthfulQA_mc2, ARC-Easy
- Decoding: loglikelihood scoring (no free generation)
- Seeds: {0, 1, 2}
- Quantization (runtime): 4-bit NF4, compute_dtype = bfloat16

## Results (post-QLoRA)

Source of truth:

- Aggregated post metrics: `evals/postqlora/summary_postqlora_aggregated.csv`
- Pre/post deltas + CI/p-values (seed 0 reference): `evals/comparison/experiment_matrix_seed0.csv` (also exported to `docs/experiment_matrix_seed0.md`)

Mean over seeds {0,1,2}:

- TruthfulQA_mc2:
  - acc_post = 0.552496
  - HR_TQA_post = 1 − acc_post = 0.447504
  - Δacc_tqa (post − pre) = +0.0525914
  - 95% CI for Δacc_tqa (paired bootstrap) = [+0.039571, +0.065811]

- ARC-Easy:
  - acc_norm_post = 0.839646
  - Δacc_norm (post − pre) = +0.0551347
  - McNemar exact p-value (seed 0) = 2.29552e-21
