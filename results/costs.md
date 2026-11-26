Measured on NVIDIA H100 PCIe MIG 3g.40gb, model Qwen/Qwen2.5-7B-Instruct, clean test queries (n=48). Medians. Absolute times depend on the hardware; compare each defense with the LLM call.

| Defense | Extra work per query | Extra time per query |
|---|---|---|
| Spotlighting | +178 prompt tokens (+54%) | LLM call 3.95 s vs 4.40 s without |
| Detector | 3.5 classifier calls | 320 ms on CPU, 15 ms on GPU |
| Sink allowlist | one HTML parse of the answer | 0.48 ms on CPU |
| (reference) LLM call | - | 4.40 s (batch 1, up to 512 new tokens) |
