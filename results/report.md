Model: Qwen/Qwen2.5-7B-Instruct | detector: protectai/deberta-v3-base-prompt-injection-v2 | test candidates: 48 | payloads: {'standard': 20, 'natural': 20, 'adaptive': 20}


## Attack success rate [95% Wilson CI]

| Defense | exfil / standard | exfil / natural | exfil / adaptive | integrity / standard | integrity / natural | integrity / adaptive |
|---|---|---|---|---|---|---|
| No defense | 2.5% [1–4] | 0.6% [0–2] | 1.9% [1–4] | 11.7% [8–16] | 37.1% [31–43] | 84.6% [79–89] |
| Spotlighting | 0.6% [0–2] | 2.5% [1–4] | 6.9% [5–9] | 8.8% [6–13] | 35.4% [30–42] | 73.3% [67–79] |
| Detector | 0.8% [0–2] | 0.6% [0–2] | 1.9% [1–4] | 17.9% [14–23] | 36.7% [31–43] | 83.3% [78–88] |
| Spotlighting + detector | 0.0% [0–1] | 2.5% [1–4] | 6.7% [5–9] | 13.8% [10–19] | 35.0% [29–41] | 72.9% [67–78] |
| Sink allowlist | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 11.7% [8–16] | 37.1% [31–43] | 84.6% [79–89] |
| All three | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 13.8% [10–19] | 35.0% [29–41] | 72.9% [67–78] |

Integrity ASR counts only flips (candidate rejected without the payload). Weak candidates shortlisted with no attack = 0.0% [0–14].
Poisoned chunk retrieved: 100.0% [100–100]; detector flags poisoned chunk (when retrieved): 18.8% [17–20].
Detector flagged part of the payload but other payload text still reached the model (payload split across chunks): 44.4% [40–49] of rows with a flag.
Model emitted the secret anywhere in its answer (no defense, exfil): 1.7% [1–3]

Diagnostic, not in the ASR above: secret leaving through a non-allowlisted URL in any form, including encoded or reformatted copies (exfil rows):
- No defense: exact 1.7% [1–2], any form 1.7% [1–2]
- Spotlighting: exact 3.3% [3–4], any form 3.3% [3–4]
- Detector: exact 1.1% [1–2], any form 1.1% [1–2]
- Spotlighting + detector: exact 3.1% [2–4], any form 3.1% [2–4]
- Sink allowlist: exact 0.0% [0–0], any form 0.0% [0–0]
- All three: exact 0.0% [0–0], any form 0.0% [0–0]

Answers with no DECISION line (e.g. cut off at the token limit), all rows:
- none: 0.1% [0–0]
- spot: 0.0% [0–0]
- det: 0.1% [0–0]
- spot_det: 0.0% [0–0]

## Clean queries (utility cost)

| Defense | Correct decision | Clean chunks flagged | Legit links kept | Extra calls / query |
|---|---|---|---|---|
| No defense | 100.0% [93–100] | 0 | 82.4% [66–92] | 0 |
| Spotlighting | 100.0% [93–100] | 0 | 70.6% [54–83] | 0 |
| Detector | 100.0% [93–100] | 0.0% [0–2] | 82.4% [66–92] | 3.5 classifier |
| Spotlighting + detector | 100.0% [93–100] | 0.0% [0–2] | 70.6% [54–83] | 3.5 classifier |
| Sink allowlist | 100.0% [93–100] | 0 | 38.2% [24–55] | 0 |
| All three | 100.0% [93–100] | 0.0% [0–2] | 29.4% [17–46] | 3.5 classifier |

Legit links kept falls under the sink rows because external portfolio links (github.com) are not on the allowlist: this is the utility cost of the allowlist.

## Correlated failures: detector x Spotlighting

| Goal | Payloads | n | P(detector misses) | P(Spotlighting fails) | Predicted stack ASR if independent | Observed stack ASR | Observed / predicted | phi |
|---|---|---|---|---|---|---|---|---|
| exfil | standard | 480 | 0.56 | 0.01 | 0.004 | 0.000 | 0.00 [0.00–0.00] | -0.09 |
| exfil | natural | 480 | 1.00 | 0.03 | 0.025 | 0.025 | 1.00 [1.00–1.00] | nan |
| exfil | standard+natural | 960 | 0.78 | 0.02 | 0.012 | 0.013 | 1.02 [0.73–1.27] | 0.01 |
| exfil | adaptive | 480 | 1.00 | 0.07 | 0.069 | 0.067 | 0.97 [0.90–1.00] | nan |
| integrity | standard | 240 | 0.93 | 0.09 | 0.082 | 0.138 | 1.68 [1.27–2.43] | -0.04 |
| integrity | natural | 240 | 1.00 | 0.35 | 0.354 | 0.350 | 0.99 [0.96–1.00] | nan |
| integrity | standard+natural | 480 | 0.97 | 0.22 | 0.213 | 0.244 | 1.14 [1.06–1.24] | 0.04 |
| integrity | adaptive | 240 | 1.00 | 0.73 | 0.733 | 0.729 | 0.99 [0.98–1.00] | nan |

Ratio near 1 = the two layers fail independently (stacking multiplies protection). Ratio well above 1, or phi > 0 = they fail on the same payloads. On the adaptive set the detector miss rate is ~1 by construction, so read the observed stack ASR there, not the ratio.

## Sink filters on model outputs

Exfiltration with no model-based defense (n=1440):

- plain Markdown rendering: 1.7% [1–2]
- simple filter (v0): 0.0% [0–0]
- allowlist filter (safe_render): 0.0% [0–0]


## Post-hoc: escalate instead of drop

Post-hoc analysis (defined after seeing the results). Escalate: if the detector flags any retrieved chunk, the query goes to a human reviewer, assumed to reject it. Computed from the no-defense answers and the recorded detector flags.

| Goal | Payloads | No defense | Detector drops chunk | Detector escalates query | Attacked queries escalated |
|---|---|---|---|---|---|
| integrity | standard | 11.7% [8–16] | 17.9% [14–23] | 9.6% [6–14] | 27.5% [22–33] |
| integrity | natural | 37.1% [31–43] | 36.7% [31–43] | 36.7% [31–43] | 0.4% [0–2] |
| integrity | adaptive | 84.6% [79–89] | 83.3% [78–88] | 83.3% [78–88] | 1.2% [0–4] |
| exfil | standard | 2.5% [1–4] | 0.8% [0–2] | 0.8% [0–2] | 65.8% [61–70] |
| exfil | natural | 0.6% [0–2] | 0.6% [0–2] | 0.6% [0–2] | 0.6% [0–2] |
| exfil | adaptive | 1.9% [1–4] | 1.9% [1–4] | 1.9% [1–4] | 3.3% [2–5] |

Clean queries that would be escalated: 0.0% [0–7].