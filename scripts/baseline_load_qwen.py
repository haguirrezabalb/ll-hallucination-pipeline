#!/usr/bin/env python3
"""
scripts/baseline_load_qwen.py

Purpose:
- Smoke test: load the base model with 4-bit NF4 quantization and run a short deterministic generation.

Inputs:
- MODEL_PATH (env var): local Hugging Face model directory (e.g., Qwen3-8B-Base)

Output:
- Prints a short generated completion to stdout.

Notes:
- Uses BitsAndBytesConfig (preferred over deprecated load_in_4bit flags).
- trust_remote_code=True is required for Qwen-family implementations.
"""

import os
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def get_model_path() -> str:
    # Read the base model checkpoint path from an environment variable (no hardcoded local paths).
    model_path: Optional[str] = os.environ.get("MODEL_PATH")
    if not model_path:
        raise RuntimeError(
            "Environment variable MODEL_PATH is not set.\n"
            "Example:\n"
            "  export MODEL_PATH=/path/to/model/Qwen3-8B-Base"
        )
    return model_path


def main() -> None:
    model_path = get_model_path()
    print(f"[baseline_load_qwen] Loading model from MODEL_PATH={model_path}")

    # 4-bit NF4 quantized loading (bitsandbytes):
    # - NF4: recommended 4-bit quantization for LLM weights
    # - compute dtype: BF16 for matmul/accumulation
    # - double quant: reduces memory overhead for quantization constants
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load tokenizer (trust_remote_code is common/required for Qwen-family models).
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # Load model with quantization_config and place it on the available device(s).
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )

    # Minimal prompt to validate inference works end-to-end.
    prompt = "Write a short sentence about language model evaluation:"

    # Tokenize to PyTorch tensors and move inputs to the model device.
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # Some tokenizers do not define a PAD token; fall back to EOS if needed.
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        pad_id = tokenizer.eos_token_id
    else:
        pad_id = tokenizer.pad_token_id

    # Deterministic generation to keep this a stable smoke test.
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=64,
            do_sample=False,
            temperature=0.0,
            top_p=1.0,
            pad_token_id=pad_id,
        )

    generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    print("\n[baseline_load_qwen] Generated output:")
    print(generated)


if __name__ == "__main__":
    main()
