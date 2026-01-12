# Runbook — ll-hallucination-pipeline

This runbook documents how to reproduce the full pipeline (baseline → QLoRA SFT → post-QLoRA evaluation → analysis).

## 0) Preconditions

### Environment manager

- Dependencies are pinned via `uv.lock`.

### Required environment variables

WSL CUDA runtime (recommended):
`export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH`

Local model path (do not hardcode it in scripts):
`export MODEL_PATH=/home/USER/models/qwen3-8b-base/Qwen3-8B-Base`

Optional offline mode (recommended when using a local checkpoint):

```bash
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
```

## 1) Setup (uv)

`uv sync`

## 2) Baseline (pre-QLoRA / pre-adapter)

Step 1) Snapshot the GPU
`nvidia-smi > docs/nvidia-smi.txt`

Step 2) Snapshot the Python / Torch environment
`uv run python scripts/dump_torch_env.py > docs/torch_env.txt`

Step 3) Smoke test: load Qwen3-8B-Base in 4-bit NF4
`uv run python scripts/baseline_load_qwen.py`

Step 4) Run baseline evaluation (tasks × seeds)

Wrapper script (recommended):

`uv run python scripts/run_lm_eval_baseline.py`

Optional: direct lm-eval-harness CLI (repeat with S=0,1,2).

TruthfulQA_mc2:

```bash
uv run python -m lm_eval \
  --model hf \
  --model_args "pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,trust_remote_code=True,load_in_4bit=True,bnb_4bit_quant_type=nf4,bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=bfloat16,dtype=bfloat16" \
  --tasks truthfulqa_mc2 \
  --num_fewshot 0 \
  --batch_size auto \
  --max_batch_size 4 \
  --seed S,S,S,S \
  --output_path evals/baseline/truthfulqa_mc2_seedS_full \
  --log_samples
```

ARC-Easy:

```bash
uv run python -m lm_eval \
  --model hf \
  --model_args "pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,trust_remote_code=True,load_in_4bit=True,bnb_4bit_quant_type=nf4,bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=bfloat16,dtype=bfloat16" \
  --tasks arc_easy \
  --num_fewshot 0 \
  --batch_size auto \
  --max_batch_size 4 \
  --seed S,S,S,S \
  --output_path evals/baseline/arc_easy_seedS_full \
  --log_samples
```

Step 5) Summarize baseline results (CSV)

`uv run python scripts/summarize_baseline.py`

Step 6) Bootstrap confidence intervals (baseline)

`uv run python scripts/run_bootstrap_baseline.py`

## 3) Draft runs (never mix with final results)

Example (limit 10):

```bash
uv run python -m lm_eval \
  --model hf \
  --model_args "pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,trust_remote_code=True,load_in_4bit=True,bnb_4bit_quant_type=nf4,bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=bfloat16,dtype=bfloat16" \
  --tasks truthfulqa_mc2 \
  --num_fewshot 0 \
  --batch_size auto \
  --max_batch_size 4 \
  --seed 0,0,0,0 \
  --limit 10 \
  --output_path evals/drafts/truthfulqa_mc2_seed0_limit10 \
  --log_samples
```

## 4) QLoRA training (SFT)

Training produces adapter directories (PEFT) that are later loaded for post-QLoRA evaluation.
Configs live in configs/qlora_*.toml.

Example:

`uv run python scripts/train_qlora.py --config configs/qlora_alpaca_10k.toml`

After training, export the adapter path for evaluation:

`export LORA_ADAPTER_PATH=/path/to/the/generated/adapter_dir`

## 5) Post-QLoRA evaluation (adapter loaded)

Step 1) Run post-QLoRA evaluation (tasks × seeds × adapters)
`uv run python scripts/run_lm_eval_postqlora.py`

Optional: direct lm-eval-harness CLI (repeat with S=0,1,2):

```bash
uv run python -m lm_eval \
  --model hf \
  --model_args "pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,trust_remote_code=True,load_in_4bit=True,bnb_4bit_quant_type=nf4,bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=bfloat16,dtype=bfloat16,peft=$LORA_ADAPTER_PATH" \
  --tasks truthfulqa_mc2 \
  --num_fewshot 0 \
  --batch_size auto \
  --max_batch_size 4 \
  --seed S,S,S,S \
  --output_path evals/postqlora/truthfulqa_mc2_seedS_full \
  --log_samples
```

Step 2) Summarize post-QLoRA results (CSV)

`uv run python scripts/summarize_postqlora.py`

Step 3) Compare pre vs post (deltas)

`uv run python scripts/compare_pre_post.py`

Step 4) Paired significance test (ARC-Easy, McNemar)

`uv run python scripts/mcnemar_from_samples.py`

Step 5) Paired bootstrap for TruthfulQA deltas (seed 0)

`uv run python scripts/paired_bootstrap_truthfulqa.py`

## 6) Regeneration quick checklist (after running lm-eval)

From the repository root:

## Summaries

```bash
uv run python scripts/summarize_baseline.py
uv run python scripts/summarize_postqlora.py

# Symlink view by adapter
uv run python scripts/build_postqlora_by_adapter_links.py

# Pre/post comparison
uv run python scripts/compare_pre_post.py

# Statistics (seed 0)
uv run python scripts/mcnemar_from_samples.py
uv run python scripts/paired_bootstrap_truthfulqa.py

# Exports and figures
uv run python scripts/export_qlora_recipe_table.py
uv run python scripts/export_experiment_matrix.py
uv run python scripts/export_delta_summary_for_plots.py
uv run python scripts/tradeoff_scatter.py

# Qualitative dumps (examples)
uv run python scripts/generate_qualitative_cases_pre.py
```

## 7) Inspecting logs (qualitative analysis)

Per-item logs live in:

`evals/**/samples_*.jsonl`

Quick inspection:

```bash
head -n 20 evals/baseline/truthfulqa_mc2_seed0_full/samples_*.jsonl
less evals/baseline/truthfulqa_mc2_seed0_full/samples_*.jsonl
```

## 8) Documentation policy (manual vs generated)

Manual (edited by hand):

`docs/eval_card_pre.md` (baseline evaluation card)

`docs/eval_card_post.md` (post-QLoRA evaluation card)

Generated (regenerable, derived from evals/ and configs/):

`docs/qlora_training_recipe.md / .csv` (from scripts/export_qlora_recipe_table.py)

`docs/experiment_matrix_seed0.md` (from scripts/export_experiment_matrix.py)

`docs/figures/tradeoff_scatter.*` (from scripts/tradeoff_scatter.py)

`docs/qualitative_*.md` (from s`cripts/generate_qualitative_*.py`)

Typically not versioned (often large/regenerable):

`evals/**` raw outputs (`results_*.json`, `samples_*.jsonl`) and derived CSVs, depending on repo policy

Backbone checkpoints and LoRA adapters under user paths (e.g., `~/models/...`)
