#!/usr/bin/env python
"""
QLoRA training for Qwen3-8B-Base using configs/qlora.toml.

- Load the base model in 4-bit NF4 with bf16 compute.
- Apply LoRA adapters according to the config.
- Train using transformers + peft + bitsandbytes.
- Save the adapters to lora_output_dir.

Typical run:

    uv run python scripts/train_qlora.py \
        --config configs/qlora.toml \
        --max_train_samples 512   # optional (smoke test)

"""

import argparse
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import torch
from datasets import Dataset, DatasetDict, load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
    set_seed,
)

# Utilities to read configs/qlora.toml (simple parser)

def _parse_toml_value(raw: str) -> Any:
    """
    Small TOML value parser for this project.
    Supports:
      - quoted strings
      - bool (true / false)
      - int, float
      - lists of the above
    """
    raw = raw.strip()

    # List
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items: List[str] = [x.strip() for x in inner.split(",")]
        parsed_list: List[Any] = []
        for item in items:
            parsed_list.append(_parse_toml_value(item))
        return parsed_list

    # Quoted string
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]

    lower = raw.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False

    # Int
    try:
        return int(raw)
    except ValueError:
        pass

    # Float
    try:
        return float(raw)
    except ValueError:
        pass

    # Fallback: literal string
    return raw

def load_qlora_config(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load configs/qlora.toml into a minimal nested dict:
        {
            "model": {...},
            "lora": {...},
            "training": {...},
            "seeds": {...},
            "output": {...},
        }
    """
    config: Dict[str, Dict[str, Any]] = {}
    current_section: Optional[str] = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Empty lines or comments
            if not line or line.startswith("#"):
                continue

            # Section [section]
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                current_section = section_name
                if section_name not in config:
                    config[section_name] = {}
                continue

            # Key = value
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                # Strip inline comments
                value = value.split("#", 1)[0].strip()
                parsed_value = _parse_toml_value(value)

                if current_section is None:
                    # Root-level key (not expected, but handled)
                    if "" not in config:
                        config[""] = {}
                    config[""][key] = parsed_value
                else:
                    config[current_section][key] = parsed_value

    return config


# Dataset and preprocessing


@dataclass
class QLoRADatasetConfig:
    dataset_type: str
    dataset_path: str
    instruction_column: Optional[str]
    input_column: Optional[str]
    output_column: Optional[str]
    max_seq_length: int
    padding_side: str
    truncation: str


def load_and_prepare_datasets(
    cfg: QLoRADatasetConfig,
    tokenizer,
    max_train_samples: Optional[int] = None,
    max_eval_samples: Optional[int] = None,
) -> Dict[str, Optional[Dataset]]:
    """
    Load the dataset with `datasets` and apply tokenization.
    Supports:
      - dataset_type == "jsonl": local .jsonl path
      - dataset_type == "parquet": local .parquet path
      - dataset_type == "hf": dataset name on the Hugging Face Hub
    Returns a dict with train and eval (eval may be None).
    """
    dataset_type = cfg.dataset_type.lower()

    if dataset_type == "jsonl":
        raw_datasets: Union[Dataset, DatasetDict] = load_dataset(
            "json", data_files={"train": cfg.dataset_path}
        )
    elif dataset_type == "parquet":
        raw_datasets = load_dataset("parquet", data_files={"train": cfg.dataset_path})
    elif dataset_type == "hf":
        raw_datasets = load_dataset(cfg.dataset_path)
    else:
        raise ValueError(f"Unknown dataset_type: {cfg.dataset_type}")

    if isinstance(raw_datasets, DatasetDict):
        train_dataset = raw_datasets["train"]
        eval_dataset = raw_datasets["validation"] if "validation" in raw_datasets else None
    else:
        train_dataset = raw_datasets
        eval_dataset = None

    def build_text(example: Dict[str, Any]) -> str:
        # Build a single text sequence from instruction, optional input, and expected output.
        parts: List[str] = []

        if cfg.instruction_column and cfg.instruction_column in example:
            instr = example.get(cfg.instruction_column)
            if instr:
                parts.append(f"Instruction:\n{instr}")

        if cfg.input_column and cfg.input_column in example:
            inp = example.get(cfg.input_column)
            if inp:
                parts.append(f"Input:\n{inp}")

        if cfg.output_column and cfg.output_column in example:
            out = example.get(cfg.output_column)
            if out:
                parts.append(f"Expected answer:\n{out}")

        if not parts:
            # Fallback to a generic "text" field if present
            if "text" in example and example["text"]:
                return str(example["text"])
            raise ValueError("Example has no recognized text columns")

        return "\n\n".join(parts)

    def preprocess_function(examples: Dict[str, List[Any]]) -> Dict[str, Any]:
        # Build texts from a batched examples dict
        num_examples = len(next(iter(examples.values())))
        texts: List[str] = []
        for i in range(num_examples):
            ex = {k: v[i] for k, v in examples.items()}
            texts.append(build_text(ex))

        model_inputs = tokenizer(
            texts,
            max_length=cfg.max_seq_length,
            truncation=True,
            padding="max_length",
        )
        # Labels equal to input_ids for causal LM training
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs

    # Tokenize
    train_dataset = train_dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=train_dataset.column_names,
    )

    if max_train_samples is not None and max_train_samples > 0:
        max_train_samples = min(max_train_samples, len(train_dataset))
        # NOTE: Deterministic prefix subset (no shuffle) for strict reproducibility.
        # If wanted randomized subsets (non-deterministic w.r.t. dataset ordering), shuffle before selecting:
        #   train_dataset = train_dataset.shuffle(seed=<data_seed from config>)
        #   train_dataset = train_dataset.select(range(max_train_samples))
        # IMPORTANT: switching to shuffled subsets will change the training data and will invalidate
        # any previously reported results unless you re-run all trainings and analyses.
        train_dataset = train_dataset.select(range(max_train_samples))

    if eval_dataset is not None:
        eval_dataset = eval_dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=eval_dataset.column_names,
        )
        if max_eval_samples is not None and max_eval_samples > 0:
            max_eval_samples = min(max_eval_samples, len(eval_dataset))
            eval_dataset = eval_dataset.select(range(max_eval_samples))

    return {"train": train_dataset, "eval": eval_dataset}


# Model, LoRA, and training

def build_model_and_tokenizer(
    cfg: Dict[str, Any],
    lora_cfg: Dict[str, Any],
    gradient_checkpointing: bool,
) -> Dict[str, Any]:
    # Load Qwen3-8B-Base in 4-bit NF4 with bf16 compute and apply LoRA.
    base_model_path = cfg.get("base_model_path", "$MODEL_PATH")
    base_model_path = os.path.expandvars(base_model_path)

    if not base_model_path or "$MODEL_PATH" in base_model_path:
        env_model_path = os.environ.get("MODEL_PATH", "").strip()
        if not env_model_path:
            raise RuntimeError(
                "Could not resolve base_model_path. "
                "Set MODEL_PATH or update configs/qlora.toml."
            )
        base_model_path = env_model_path

    quant_type = cfg.get("quant_type", "nf4")
    compute_dtype_str = str(cfg.get("compute_dtype", "bfloat16")).lower()
    use_double_quant = bool(cfg.get("use_double_quant", True))

    if compute_dtype_str == "bfloat16":
        compute_dtype = torch.bfloat16
    elif compute_dtype_str in ("float16", "fp16"):
        compute_dtype = torch.float16
    elif compute_dtype_str in ("float32", "fp32"):
        compute_dtype = torch.float32
    else:
        compute_dtype = torch.bfloat16

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=bool(cfg.get("load_in_4bit", True)),
        bnb_4bit_quant_type=quant_type,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=use_double_quant,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        base_model_path,
        trust_remote_code=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    model.config.pad_token_id = tokenizer.pad_token_id

    # QLoRA preparation
    if gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False

    model = prepare_model_for_kbit_training(model)

    # LoRA config
    target_modules = lora_cfg.get("target_modules", [])
    if not target_modules:
        raise ValueError("configs/qlora.toml must define lora.target_modules")

    lora_r = int(lora_cfg.get("lora_r", 64))
    lora_alpha = int(lora_cfg.get("lora_alpha", 16))
    lora_dropout = float(lora_cfg.get("lora_dropout", 0.05))

    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=target_modules,
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, peft_config)

    # Small log: trainable parameters
    trainable, total = 0, 0
    for _, p in model.named_parameters():
        numel = p.numel()
        total += numel
        if p.requires_grad:
            trainable += numel
    print(
        f"Trainable parameters: {trainable} / {total} "
        f"({100 * trainable / total:.4f} %)"
    )

    return {"model": model, "tokenizer": tokenizer}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="QLoRA training for Qwen3-8B-Base using configs/qlora.toml."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/qlora.toml",
        help="Path to the QLoRA TOML config file.",
    )
    parser.add_argument(
        "--max_train_samples",
        type=int,
        default=None,
        help="If set, limit the number of training examples (smoke test).",
    )
    parser.add_argument(
        "--max_eval_samples",
        type=int,
        default=None,
        help="If set, limit the number of validation examples.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information about the config and datasets.",
    )

    args = parser.parse_args()

    # 1) Load TOML config
    cfg = load_qlora_config(args.config)

    model_cfg = cfg.get("model", {})
    lora_cfg = cfg.get("lora", {})
    training_cfg = cfg.get("training", {})
    seeds_cfg = cfg.get("seeds", {})
    output_cfg = cfg.get("output", {})

    # Training subset size: CLI overrides TOML if provided
    max_train_samples = (
        args.max_train_samples
        if args.max_train_samples is not None
        else training_cfg.get("max_train_samples", None)
    )

    # 2) Seeds
    train_seed = int(seeds_cfg.get("train_seed", 42))
    data_seed = int(seeds_cfg.get("data_seed", 42))
    model_seed = int(seeds_cfg.get("model_seed", 42))

    random.seed(train_seed)
    np.random.seed(data_seed)
    torch.manual_seed(model_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(model_seed)
    set_seed(model_seed)

    # 3) Build model and tokenizer
    gradient_checkpointing = bool(training_cfg.get("gradient_checkpointing", True))

    mt = build_model_and_tokenizer(
        model_cfg,
        lora_cfg,
        gradient_checkpointing=gradient_checkpointing,
    )
    model = mt["model"]
    tokenizer = mt["tokenizer"]

    # Tokenizer padding/truncation settings
    padding_side = training_cfg.get("padding_side", "right")
    tokenizer.padding_side = padding_side

    # Tokenizer truncation side ("right" / "left")
    truncation_side = str(training_cfg.get("truncation", "right")).lower()
    if truncation_side in ("left", "right"):
        tokenizer.truncation_side = truncation_side

    # 4) Load and preprocess data
    dataset_cfg = QLoRADatasetConfig(
        dataset_type=str(training_cfg.get("dataset_type", "jsonl")),
        dataset_path=str(training_cfg.get("dataset_path", "")),
        instruction_column=training_cfg.get("instruction_column", "instruction"),
        input_column=training_cfg.get("input_column", "input"),
        output_column=training_cfg.get("output_column", "output"),
        max_seq_length=int(training_cfg.get("max_seq_length", 1024)),
        padding_side=str(training_cfg.get("padding_side", "right")),
        truncation=str(training_cfg.get("truncation", "right")),
    )

    if not dataset_cfg.dataset_path and dataset_cfg.dataset_type != "hf":
        raise RuntimeError(
            "dataset_path is not set in configs/qlora.toml and dataset_type is not 'hf'."
        )

    datasets_dict = load_and_prepare_datasets(
        dataset_cfg,
        tokenizer,
        max_train_samples=max_train_samples,
        max_eval_samples=args.max_eval_samples,
    )
    train_dataset = datasets_dict["train"]
    eval_dataset = datasets_dict["eval"]

    if args.debug:
        print(f"Train size: {len(train_dataset)} examples")
        if eval_dataset is not None:
            print(f"Eval size: {len(eval_dataset)} examples")
        else:
            print("No evaluation split.")

    # 5) Training arguments
    lora_output_dir = output_cfg.get(
        "lora_output_dir",
        "/tmp/qwen3-8b-qlora-adapters",
    )
    lora_output_dir = os.path.expanduser(os.path.expandvars(str(lora_output_dir)))
    os.makedirs(lora_output_dir, exist_ok=True)

    num_train_epochs = float(training_cfg.get("num_train_epochs", 3))
    max_steps = int(training_cfg.get("max_steps", -1))

    per_device_train_batch_size = int(training_cfg.get("per_device_train_batch_size", 1))
    gradient_accumulation_steps = int(training_cfg.get("gradient_accumulation_steps", 1))

    learning_rate = float(training_cfg.get("learning_rate", 2e-4))
    warmup_ratio = float(training_cfg.get("warmup_ratio", 0.03))
    weight_decay = float(training_cfg.get("weight_decay", 0.0))
    logging_steps = int(training_cfg.get("logging_steps", 10))
    save_steps = int(training_cfg.get("save_steps", 200))
    max_grad_norm = float(training_cfg.get("max_grad_norm", 0.3))

    has_eval = eval_dataset is not None

    # Note: in some transformers versions, TrainingArguments may not accept certain evaluation-related arguments. 
    # This script trains without an automatic evaluation strategy; trainer.evaluate() can be called manually if needed.
    training_args = TrainingArguments(
        output_dir=lora_output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=num_train_epochs,
        max_steps=max_steps,
        learning_rate=learning_rate,
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        logging_steps=logging_steps,
        save_steps=save_steps,
        save_total_limit=2,
        bf16=(model_cfg.get("compute_dtype", "bfloat16") == "bfloat16"),
        gradient_checkpointing=gradient_checkpointing,
        max_grad_norm=max_grad_norm,
        report_to="none",
        remove_unused_columns=False,
        logging_first_step=True,
    )

    # 6) Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if has_eval else None,
    )

    # 7) Train
    train_result = trainer.train()
    trainer.save_model(lora_output_dir)
    tokenizer.save_pretrained(lora_output_dir)

    metrics = train_result.metrics
    metrics["train_samples"] = len(train_dataset)
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    print()
    print("QLoRA training completed.")
    print(f"LoRA adapters saved to: {lora_output_dir}")
    print("Remember to set LORA_ADAPTER_PATH to this directory for post-QLoRA evaluations.")
    print()


if __name__ == "__main__":
    main()
