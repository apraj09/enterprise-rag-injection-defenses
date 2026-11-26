"""GPU checks for run_h100.pbs.

  python -m layering.preflight --pick --model M   UUID of the MIG slice with the most free memory
  python -m layering.preflight --model M          largest HF batch size that fits the pinned GPU

Exit code 3 means the run does not fit.
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

GiB = 2 ** 30
DETECTOR = 1.5 * GiB       # DeBERTa detector on the same device
OVERHEAD = 3 * GiB         # CUDA context, activations, allocator slack
TOKENS_PER_SEQ = 1600      # longest (datamarked) prompt plus up to 512 new tokens, rounded up
BATCHES = (32, 16, 8, 4)
PICK_MIN_BATCH = 8         # --pick only chooses slices that fit at least this HF batch


def log(msg: str) -> None:
    print(f"[preflight] {msg}", file=sys.stderr, flush=True)


def model_dims(model: str) -> tuple[int, int]:
    """(weight bytes, KV-cache bytes per token) from the locally cached model."""
    from huggingface_hub import snapshot_download
    from transformers import AutoConfig
    path = snapshot_download(model, local_files_only=True)
    files = glob.glob(os.path.join(path, "*.safetensors")) or glob.glob(os.path.join(path, "*.bin"))
    weights = sum(os.path.getsize(f) for f in files)
    c = AutoConfig.from_pretrained(path)
    heads = c.num_attention_heads
    kv_heads = getattr(c, "num_key_value_heads", None) or heads
    head_dim = getattr(c, "head_dim", None) or c.hidden_size // heads
    return weights, 2 * c.num_hidden_layers * kv_heads * head_dim * 2   # K and V, 2 bytes each


def need_bytes(backend: str, total: float, gpu_mem: float, weights: int, kv: int, batch: int) -> float:
    if backend == "vllm":
        return gpu_mem * total + DETECTOR
    return weights + batch * TOKENS_PER_SEQ * kv + DETECTOR + OVERHEAD


def mig_slices() -> list[tuple[str, int, int, int, int]]:
    """(uuid, gpu index, MIG device index, free bytes, total bytes) for every MIG slice."""
    try:
        import pynvml as nv
    except ImportError:
        sys.exit("[preflight] pynvml missing: pip install nvidia-ml-py")
    nv.nvmlInit()
    out = []
    for i in range(nv.nvmlDeviceGetCount()):
        h = nv.nvmlDeviceGetHandleByIndex(i)
        try:
            if nv.nvmlDeviceGetMigMode(h)[0] != 1:
                continue
        except nv.NVMLError:
            continue
        for j in range(nv.nvmlDeviceGetMaxMigDeviceCount(h)):
            try:
                m = nv.nvmlDeviceGetMigDeviceHandleByIndex(h, j)
            except nv.NVMLError:
                continue
            mem = nv.nvmlDeviceGetMemoryInfo(m)
            uuid = nv.nvmlDeviceGetUUID(m)
            out.append((uuid.decode() if isinstance(uuid, bytes) else uuid, i, j, mem.free, mem.total))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", default="vllm", choices=["vllm", "hf"])
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--max-batch", type=int, default=32)
    ap.add_argument("--pick", action="store_true")
    a = ap.parse_args()

    weights, kv = model_dims(a.model)
    log(f"{a.model}: weights {weights / GiB:.1f} GiB, KV cache {kv * TOKENS_PER_SEQ / GiB:.2f} GiB per sequence")

    if a.pick:
        fits = []
        for uuid, g, d, free, total in mig_slices():
            need = need_bytes(a.backend, total, a.gpu_mem, weights, kv, PICK_MIN_BATCH)
            ok = free >= need
            log(f"GPU {g} slice {d}: {free / GiB:.1f} of {total / GiB:.1f} GiB free, "
                f"needs {need / GiB:.1f} -> {'fits' if ok else 'too full'}")
            if ok:
                fits.append((free, uuid))
        if not fits:
            log("No MIG slice has enough free memory right now. Try again later or use a smaller model.")
            sys.exit(3)
        print(max(fits)[1])
        return

    import torch
    free, total = torch.cuda.mem_get_info(0)
    log(f"{torch.cuda.get_device_name(0)}: {total / GiB:.1f} GiB total, {free / GiB:.1f} GiB free")
    batch = next((b for b in BATCHES if b <= a.max_batch
                  and need_bytes("hf", total, a.gpu_mem, weights, kv, b) <= free), 0)
    if a.backend == "vllm":
        need = need_bytes("vllm", total, a.gpu_mem, weights, kv, 0)
        log(f"vLLM needs about {need / GiB:.1f} GiB; HF fallback batch size: {batch or 'does not fit'}")
        ok = free >= need
    else:
        log(f"HF backend: largest batch size that fits = {batch or 'none'}")
        ok = batch > 0
    if not ok:
        log("Not enough free GPU memory on this device (another process is using it). "
            "Use another slice, GPU=auto, or a smaller model.")
        sys.exit(3)
    print(batch or 1)


if __name__ == "__main__":
    main()
