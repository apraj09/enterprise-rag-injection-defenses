Measured on NVIDIA H100 NVL MIG 3g.47gb, model Qwen/Qwen2.5-14B-Instruct, clean test queries (n=48). Medians. Absolute times depend on the hardware; compare each defense with the LLM call.

| Defense | Extra work per query | Extra time per query |
|---|---|---|
| Spotlighting | +178 prompt tokens (+54%) | LLM call 4.71 s vs 5.08 s without |
| Detector | 3.5 classifier calls | 303 ms on CPU, 31 ms on GPU |
| Sink allowlist | one HTML parse of the answer | 0.27 ms on CPU |
| (reference) LLM call | - | 5.08 s (batch 1, up to 512 new tokens) |
