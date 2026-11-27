Model: Qwen/Qwen2.5-14B-Instruct | detector: protectai/deberta-v3-base-prompt-injection-v2 | test candidates: 48 | payloads: {'standard': 20, 'natural': 20, 'adaptive': 20}


## Attack success rate [95% Wilson CI]

| Defense | exfil / standard | exfil / natural | exfil / adaptive | integrity / standard | integrity / natural | integrity / adaptive |
|---|---|---|---|---|---|---|
| No defense | 14.6% [12–18] | 1.9% [1–4] | 5.2% [4–8] | 34.2% [28–40] | 45.0% [39–51] | 70.0% [64–75] |
| Spotlighting | 4.4% [3–7] | 1.0% [0–2] | 0.8% [0–2] | 25.0% [20–31] | 41.7% [36–48] | 65.4% [59–71] |
| Detector | 0.4% [0–2] | 1.7% [1–3] | 5.2% [4–8] | 36.7% [31–43] | 44.6% [38–51] | 68.8% [63–74] |
| Spotlighting + detector | 0.0% [0–1] | 1.0% [0–2] | 0.8% [0–2] | 28.3% [23–34] | 41.2% [35–48] | 64.2% [58–70] |
| Sink allowlist | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 34.2% [28–40] | 45.0% [39–51] | 70.0% [64–75] |
| All three | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 28.3% [23–34] | 41.2% [35–48] | 64.2% [58–70] |

Integrity ASR counts only flips (candidate rejected without the payload). Weak candidates shortlisted with no attack = 0.0% [0–14].
Poisoned chunk retrieved: 100.0% [100–100]; detector flags poisoned chunk (when retrieved): 18.4% [17–20].
Detector flagged part of the payload but other payload text still reached the model (payload split across chunks): 43.3% [39–48] of rows with a flag.
Model emitted the secret anywhere in its answer (no defense, exfil): 7.4% [6–9]
Secret in the answer but in no attacker link (exfil rows, four model conditions): 0.1% [0–0]

Diagnostic, not in the ASR above: secret leaving through a non-allowlisted URL in any form, including encoded or reformatted copies (exfil rows):
- No defense: exact 7.2% [6–9], any form 7.2% [6–9]
- Spotlighting: exact 2.1% [1–3], any form 2.1% [1–3]
- Detector: exact 2.4% [2–3], any form 2.4% [2–3]
- Spotlighting + detector: exact 0.6% [0–1], any form 0.6% [0–1]
- Sink allowlist: exact 0.0% [0–0], any form 0.0% [0–0]
- All three: exact 0.0% [0–0], any form 0.0% [0–0]

Answers with no DECISION line (e.g. cut off at the token limit), all rows:
- none: 0.4% [0–1]
- spot: 0.0% [0–0]
- det: 0.0% [0–0]
- spot_det: 0.0% [0–0]

## Clean queries (utility cost)

| Defense | Correct decision | Clean chunks flagged | Legit links kept | Extra calls / query |
|---|---|---|---|---|
| No defense | 100.0% [93–100] | 0 | 79.4% [63–90] | 0 |
| Spotlighting | 100.0% [93–100] | 0 | 29.4% [17–46] | 0 |
| Detector | 100.0% [93–100] | 0.0% [0–2] | 79.4% [63–90] | 3.5 classifier |
| Spotlighting + detector | 100.0% [93–100] | 0.0% [0–2] | 29.4% [17–46] | 3.5 classifier |
| Sink allowlist | 100.0% [93–100] | 0 | 32.4% [19–49] | 0 |
| All three | 100.0% [93–100] | 0.0% [0–2] | 14.7% [6–30] | 3.5 classifier |

Legit links kept falls under the sink rows because external portfolio links (github.com) are not on the allowlist: this is the utility cost of the allowlist.

## Correlated failures: detector x Spotlighting

| Goal | Payloads | n | P(detector misses) | P(Spotlighting fails) | Predicted stack ASR if independent | Observed stack ASR | Observed / predicted | phi | Ratio CI, resampling applicants | Ratio CI, resampling payloads |
|---|---|---|---|---|---|---|---|---|---|---|
| exfil | standard | 480 | 0.56 | 0.04 | 0.025 | 0.000 | 0.00 [0.00–0.00] | -0.24 | [0.00–0.00] | [0.00–0.00] |
| exfil | natural | 480 | 1.00 | 0.01 | 0.010 | 0.010 | 1.00 [1.00–1.00] | nan | [1.00–1.00] | [1.00–1.00] |
| exfil | standard+natural | 960 | 0.78 | 0.03 | 0.021 | 0.005 | 0.25 [0.06–0.46] | -0.24 | [0.07–0.39] | [0.00–1.38] |
| exfil | adaptive | 480 | 1.00 | 0.01 | 0.008 | 0.008 | 1.00 [1.00–1.00] | nan | [1.00–1.00] | [1.00–1.00] |
| integrity | standard | 240 | 0.93 | 0.25 | 0.233 | 0.283 | 1.21 [1.06–1.42] | -0.12 | [1.04–1.46] | [0.97–1.69] |
| integrity | natural | 240 | 1.00 | 0.42 | 0.417 | 0.412 | 0.99 [0.97–1.00] | nan | [0.97–1.00] | [0.97–1.00] |
| integrity | standard+natural | 480 | 0.97 | 0.33 | 0.322 | 0.348 | 1.08 [1.02–1.15] | -0.04 | [1.02–1.15] | [0.99–1.26] |
| integrity | adaptive | 240 | 1.00 | 0.65 | 0.654 | 0.642 | 0.98 [0.96–1.00] | nan | [0.94–1.00] | [0.97–1.00] |

Ratio near 1 = the two layers fail independently (stacking multiplies protection). Ratio well above 1, or phi > 0 = they fail on the same payloads. On the adaptive set the detector miss rate is ~1 by construction, so read the observed stack ASR there, not the ratio.
The bracketed ratio CI resamples applicant and payload pairs. The last two columns resample whole applicants or whole payloads instead.

## Sink filters on model outputs

Exfiltration with no model-based defense (n=1440):

- plain Markdown rendering: 7.2% [6–9]
- simple filter (v0): 0.0% [0–0]
- allowlist filter (safe_render): 0.0% [0–0]


## Post-hoc: escalate instead of drop

Post-hoc analysis (defined after seeing the results). Escalate: if the detector flags any retrieved chunk, the query goes to a human reviewer, assumed to reject it. Computed from the no-defense answers and the recorded detector flags.

| Goal | Payloads | No defense | Detector drops chunk | Detector escalates query | Attacked queries escalated |
|---|---|---|---|---|---|
| integrity | standard | 34.2% [28–40] | 36.7% [31–43] | 27.5% [22–33] | 27.5% [22–33] |
| integrity | natural | 45.0% [39–51] | 44.6% [38–51] | 44.6% [38–51] | 0.4% [0–2] |
| integrity | adaptive | 70.0% [64–75] | 68.8% [63–74] | 68.8% [63–74] | 1.2% [0–4] |
| exfil | standard | 14.6% [12–18] | 0.4% [0–2] | 0.4% [0–2] | 65.8% [61–70] |
| exfil | natural | 1.9% [1–4] | 1.7% [1–3] | 1.7% [1–3] | 0.6% [0–2] |
| exfil | adaptive | 5.2% [4–8] | 5.2% [4–8] | 5.2% [4–8] | 1.7% [1–3] |

Clean queries that would be escalated: 0.0% [0–7].