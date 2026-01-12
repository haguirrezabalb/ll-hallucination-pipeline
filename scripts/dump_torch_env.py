#!/usr/bin/env python3
"""
scripts/dump_torch_env.py

Purpose:
- Dump a lightweight runtime environment snapshot for reproducibility and debugging:
  Python / Torch / CUDA / bitsandbytes versions, visible GPU(s), and key env vars.

Outputs:
- Prints the environment summary to stdout (can be redirected to docs/torch_env.txt).

Notes:
- torch and bitsandbytes are optional imports: the script should still run if they are not installed.
"""

import os
import platform


def main() -> None:
    # Python version helps reproduce dependency resolution and runtime behavior.
    python_version = platform.python_version()

    # torch is optional: allow this script to run even if torch is not installed.
    try:
        import torch  # type: ignore
    except ImportError:
        torch = None  # type: ignore

    # bitsandbytes is optional: used for 4-bit quantization.
    try:
        import bitsandbytes as bnb  # type: ignore
    except ImportError:
        bnb = None  # type: ignore

    print("=== Python / Torch / CUDA Environment ===")
    print(f"Python version: {python_version}")

    if torch is not None:
        print(f"torch version: {torch.__version__}")
        print(f"torch.version.cuda: {torch.version.cuda}")
        print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
    else:
        print("torch is not available (ImportError)")

    if bnb is not None:
        print(f"bitsandbytes version: {getattr(bnb, '__version__', 'unknown')}")
    else:
        print("bitsandbytes is not available (ImportError)")

    print("\n=== GPU(s) visible to torch ===")
    if torch is not None and torch.cuda.is_available():
        num_devices = torch.cuda.device_count()
        print(f"Number of visible GPUs: {num_devices}")
        for idx in range(num_devices):
            name = torch.cuda.get_device_name(idx)
            props = torch.cuda.get_device_properties(idx)
            total_mem_gb = props.total_memory / (1024**3)
            print(f"- GPU {idx}: {name}, total memory: {total_mem_gb:.2f} GB")
    else:
        print("No GPUs are visible to torch, or torch is not available")

    print("\n=== Relevant environment variables ===")
    print(f"MODEL_PATH={os.environ.get('MODEL_PATH', '<MODEL_PATH not set>')}")
    print(f"LD_LIBRARY_PATH={os.environ.get('LD_LIBRARY_PATH', '')}")
    print(f"TRANSFORMERS_OFFLINE={os.environ.get('TRANSFORMERS_OFFLINE', '')}")


if __name__ == "__main__":
    main()
