# Evaluation Card - Post-QLoRA (Multi-adapter)

## Model

- Backbone: Qwen3-8B-Base
- Adapters: QLoRA-trained LoRA adapters (evaluated independently, one adapter per run)
- Base model path: $MODEL_PATH
- Adapter path: $LORA_ADAPTER_PATH (set per run / per adapter)
- trust_remote_code: true

## Inference configuration

Same as baseline (pre-QLoRA), to ensure comparability:

- Seeds: [0, 1, 2]
- num_fewshot: 0
- Batching: batch_size = "auto", max_batch_size = 4
- Quantization (runtime, bitsandbytes): 4-bit NF4 + double quant (bnb_4bit_quant_type=nf4,  
  bnb_4bit_use_double_quant=true), compute_dtype=bfloat16 (bnb_4bit_compute_dtype=bfloat16)
- Decoding: loglikelihood scoring (no free generation)
- Generation parameters (not used for the tasks below): do_sample = false, temperature = 0.0, top_p = 1.0, top_k = 1, max_new_tokens = 256

## Evaluation tasks

- TruthfulQA_mc2 (0-shot)
- ARC-Easy (0-shot)

## QLoRA SFT configuration (shared hyperparameters)

- Rank (r): 64
- lora_alpha: 16
- lora_dropout: 0.05
- learning_rate: 2e-4
- batch_size / grad_accum:
  - per_device_train_batch_size = 1
  - gradient_accumulation_steps = 16
  - effective batch size = 16 examples per update
- num_epochs / max_steps:
  - num_train_epochs = 3
  - max_steps = -1 (num_train_epochs is used)
- warmup_ratio: 0.03
- target_modules:
  - q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- training-time quantization (QLoRA):
  - 4-bit NF4, compute_dtype = bfloat16, use_double_quant = true

## Data artifacts

- Post-QLoRA aggregated metrics:
  - evals/postqlora/summary_postqlora_aggregated.csv
- Pre/post comparison:
  - evals/comparison/summary_pre_post_aggregated_all_adapters.csv
- Paired statistics (seed 0):
  - ARC-Easy McNemar: evals/comparison/mcnemar_arc_easy_seed0.csv
  - TruthfulQA paired bootstrap: evals/comparison/paired_bootstrap_truthfulqa_mc2_seed0.csv
- Compact export for plotting:
  - evals/comparison/delta_summary_for_plots.csv
- Raw lm-eval-harness outputs (per run):
  - results_*.json
  - samples_*.jsonl

## Baseline reference (pre-QLoRA)

Baseline is the quantized backbone (no adapter), evaluated under the same frozen protocol:

- TruthfulQA_mc2:
  - acc_pre = 0.524274 (MC2 score)
  - HR_TQA_pre = 1 − acc_pre = 0.475726
- ARC-Easy:
  - acc_norm_pre = 0.780724

## Quantitative post-QLoRA results (mean over seeds {0, 1, 2})

Notes:

- TruthfulQA_mc2: `acc_post` is the MC2 score (probability mass assigned to true options).
- HR_TQA_post is defined as: HR_TQA_post = 1 − acc_post (lower is better).
- ARC-Easy utility metric is `acc_norm_post` (higher is better).
- Deltas are computed as: Δ = mean_post − mean_pre.
  - For ARC-Easy (`acc`, `acc_norm`), Δ > 0 indicates improved utility.
  - For TruthfulQA, we report HR_TQA = 1 − acc, so Δ < 0 indicates improved factuality (lower hallucination rate).

| **Adapter**   | **TruthfulQA acc_post** | **HR_TQA_post** | **ΔHR_TQA**   | **ARC acc_norm_post** | **Δacc_norm** |
| :------------ | ----------------------: | --------------: | ------------: | --------------------: | ------------: |
| alpaca_1k     |                0.543803 |        0.456197 |     -0.019528 |              0.838384 |     +0.057660 |
| alpaca_10k    |                0.559953 |        0.440047 |     -0.035678 |              0.838805 |     +0.058081 |
| alpaca_full   |                0.568320 |        0.431680 |     -0.044046 |              0.823653 |     +0.042929 |
| dolly_5k      |                0.453900 |        0.546100 |     +0.070374 |              0.820286 |     +0.039562 |
| dolly_full    |                0.445125 |        0.554875 |     +0.079150 |              0.843013 |     +0.062290 |

### Summary (observed trade-offs)

- Alpaca adapters reduce HR_TQA (better TruthfulQA_mc2 factuality proxy) and improve ARC-Easy utility.
  - Largest HR_TQA reduction: alpaca_full (ΔHR_TQA ≈ -0.0440).
  - Largest ARC acc_norm gain: alpaca_10k (Δacc_norm ≈ +0.0581).
- Dolly adapters improve ARC-Easy acc_norm but increase HR_TQA (worse TruthfulQA_mc2), suggesting a truthfulness/utility trade-off depending on the SFT dataset.
