# QLoRA training recipe (summary)

This file is generated from `configs/qlora_*.toml`.
For the full table (all fields), see `docs/qlora_training_recipe.csv`.

## Shared settings (identical across all configs)

- quantization: load_in_4bit=True, quant_type=nf4, compute_dtype=bfloat16, use_double_quant=True
- lora: lora_r=64, lora_alpha=16, lora_dropout=0.05, bias=none, target_modules=q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- training: num_train_epochs=3, max_steps=-1, learning_rate=0.0002, warmup_ratio=0.03, weight_decay=0.0, per_device_train_batch_size=1, gradient_accumulation_steps=16, effective_batch_size=16, max_grad_norm=0.3, gradient_checkpointing=True
- seeds: train_seed=42, data_seed=42, model_seed=42

## Per-condition settings

Note: `lora_output_dir` is shown as the adapter folder name (basename). Full paths are in `docs/qlora_training_recipe.csv`.

| condition | dataset_type | dataset_path | max_seq_length | adapter_dir |
| --- | --- | --- | --- | --- |
| alpaca_1k | hf | yahma/alpaca-cleaned | 1024 | qwen3-8b-base-qlora-alpaca-1k |
| alpaca_10k | hf | yahma/alpaca-cleaned | 1024 | qwen3-8b-base-qlora-alpaca-10k |
| alpaca_full | hf | yahma/alpaca-cleaned | 1024 | qwen3-8b-base-qlora-alpaca-full |
| dolly_5k | jsonl | docs/datasets/dolly_5k.jsonl | 1024 | qwen3-8b-base-qlora-dolly-5k |
| dolly_full | jsonl | docs/datasets/dolly_5k.jsonl | 1024 | qwen3-8b-base-qlora-dolly-full |
| smoketest | jsonl | docs/datasets/qlora_sft_smoketest.jsonl | 1024 | qwen3-8b-base-qlora-smoketest |
