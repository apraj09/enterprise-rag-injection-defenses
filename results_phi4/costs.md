Measured on NVIDIA H100 NVL MIG 3g.47gb, model microsoft/phi-4, clean test queries (n=48). Medians. Absolute times depend on the hardware; compare each defense with the LLM call.

| Defense | Extra work per query | Extra time per query |
|---|---|---|
| Spotlighting | +298 prompt tokens (+91%) | LLM call 3.84 s vs 4.04 s without |
| Detector | 3.5 classifier calls | 307 ms on CPU, 13 ms on GPU |
| Sink allowlist | one HTML parse of the answer | 1.22 ms on CPU |
| (reference) LLM call | - | 4.04 s (batch 1, up to 512 new tokens) |
