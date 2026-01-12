# Evaluation Card - Baseline (Pre-QLoRA / Pre-Adapter)

## Model

- Backbone: Qwen3-8B-Base
- Local path: $MODEL_PATH
- trust_remote_code: true

## Inference configuration

- Seeds: [0, 1, 2] (passed to lm-eval as "s,s,s,s" for python/numpy/torch/fewshot)
- num_fewshot: 0
- Batching: batch_size = "auto", max_batch_size = 4
- Quantization (runtime, bitsandbytes): 4-bit NF4 + double quant (bnb_4bit_quant_type=nf4,
  bnb_4bit_use_double_quant=true), compute_dtype=bfloat16 (bnb_4bit_compute_dtype=bfloat16)
- Multiple-choice decoding: loglikelihood (scoring only; no free generation)
- Generation parameters: do_sample = false, temperature = 0.0, top_p = 1.0, top_k = 1, max_new_tokens = 256 (not used for the tasks below)

## Evaluation tasks

- TruthfulQA_mc2 (0-shot)
- ARC-Easy (0-shot)

## Data artifacts

- Baseline aggregated metrics:
  - evals/baseline/summary_preqlora_aggregated.csv
- Baseline per-seed metrics:
  - evals/baseline/summary_preqlora_per_seed.csv
- Raw lm-eval-harness outputs (per run):
  - results_*.json
  - samples_*.jsonl

## Notes

- This is a pre-adapter baseline: no LoRA/QLoRA adapter weights are applied.
- The backbone is intentionally loaded in 4-bit NF4 at inference time so that pre/post comparisons share the same quantized runtime conditions.
- Bootstrap 95% confidence intervals (CIs) below are computed from per-sample logs (`samples_*.jsonl`) using the baseline seed 0 run as reference.
- With 0-shot loglikelihood scoring, seeds are expected to have no effect (seeds mainly matter for few-shot sampling and/or stochastic decoding). Across seeds {0, 1, 2}, the aggregated metrics are numerically identical for both tasks under this protocol.

## Baseline results (mean over seeds {0, 1, 2})

### TruthfulQA_mc2 (0-shot, HR_TQA_pre = 1 − acc)

- Task: `truthfulqa_mc2`
- Seeds: 0, 1, 2
- MC2 score (acc; probability mass on true options): 0.524274
- 95% CI (bootstrap, seed 0): [0.494466, 0.553722]
- HR_TQA_pre (1 − acc): 0.475726
- HR_TQA_pre 95% CI (linear transform of acc CI): [0.446278, 0.505534]
- n_samples: 817

### ARC-Easy (0-shot)

- Task: `arc_easy`
- Seeds: 0, 1, 2
- Accuracy (acc): 0.794192
- 95% CI (bootstrap, seed 0): [0.777778, 0.810185]
- Normalized accuracy (acc_norm): 0.780724
- n_samples: 2376

- Baseline CIs were computed with `run_bootstrap_baseline` over `evals/baseline/samples_*.jsonl` (see console output for the per-seed summary).
