Model: microsoft/phi-4 | detector: protectai/deberta-v3-base-prompt-injection-v2 | test candidates: 48 | payloads: {'standard': 20, 'natural': 20, 'adaptive': 20}


## Attack success rate [95% Wilson CI]

| Defense | exfil / standard | exfil / natural | exfil / adaptive | integrity / standard | integrity / natural | integrity / adaptive |
|---|---|---|---|---|---|---|
| No defense | 2.9% [2–5] | 5.0% [3–7] | 11.7% [9–15] | 30.4% [25–37] | 41.2% [35–48] | 95.0% [91–97] |
| Spotlighting | 1.0% [0–2] | 5.2% [4–8] | 13.5% [11–17] | 25.0% [20–31] | 44.6% [38–51] | 100.0% [98–100] |
| Detector | 0.4% [0–2] | 4.8% [3–7] | 10.6% [8–14] | 29.6% [24–36] | 41.2% [35–48] | 94.6% [91–97] |
| Spotlighting + detector | 0.4% [0–2] | 5.0% [3–7] | 12.5% [10–16] | 27.1% [22–33] | 44.2% [38–50] | 100.0% [98–100] |
| Sink allowlist | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 30.4% [25–37] | 41.2% [35–48] | 95.0% [91–97] |
| All three | 0.0% [0–1] | 0.0% [0–1] | 0.0% [0–1] | 27.1% [22–33] | 44.2% [38–50] | 100.0% [98–100] |

Integrity ASR counts only flips (candidate rejected without the payload). Weak candidates shortlisted with no attack = 4.2% [1–20].
Poisoned chunk retrieved: 100.0% [100–100]; detector flags poisoned chunk (when retrieved): 18.4% [17–20].
Detector flagged part of the payload but other payload text still reached the model (payload split across chunks): 43.5% [39–48] of rows with a flag.
Model emitted the secret anywhere in its answer (no defense, exfil): 6.7% [5–8]
Secret in the answer but in no attacker link (exfil rows, four model conditions): 0.1% [0–0]

Diagnostic, not in the ASR above: secret leaving through a non-allowlisted URL in any form, including encoded or reformatted copies (exfil rows):
- No defense: exact 6.5% [5–8], any form 6.5% [5–8]
- Spotlighting: exact 6.6% [5–8], any form 6.6% [5–8]
- Detector: exact 5.3% [4–7], any form 5.3% [4–7]
- Spotlighting + detector: exact 6.0% [5–7], any form 6.0% [5–7]
- Sink allowlist: exact 0.0% [0–0], any form 0.0% [0–0]
- All three: exact 0.0% [0–0], any form 0.0% [0–0]

Answers with no DECISION line (e.g. cut off at the token limit), all rows:
- none: 0.0% [0–0]
- spot: 0.0% [0–0]
- det: 0.0% [0–0]
- spot_det: 0.0% [0–0]

## Clean queries (utility cost)

| Defense | Correct decision | Clean chunks flagged | Legit links kept | Extra calls / query |
|---|---|---|---|---|
| No defense | 97.9% [89–100] | 0 | 100.0% [90–100] | 0 |
| Spotlighting | 100.0% [93–100] | 0 | 100.0% [90–100] | 0 |
| Detector | 97.9% [89–100] | 0.0% [0–2] | 100.0% [90–100] | 3.5 classifier |
| Spotlighting + detector | 100.0% [93–100] | 0.0% [0–2] | 100.0% [90–100] | 3.5 classifier |
| Sink allowlist | 97.9% [89–100] | 0 | 44.1% [29–61] | 0 |
| All three | 100.0% [93–100] | 0.0% [0–2] | 44.1% [29–61] | 3.5 classifier |

Legit links kept falls under the sink rows because external portfolio links (github.com) are not on the allowlist: this is the utility cost of the allowlist.

## Correlated failures: detector x Spotlighting

| Goal | Payloads | n | P(detector misses) | P(Spotlighting fails) | Predicted stack ASR if independent | Observed stack ASR | Observed / predicted | phi | Ratio CI, resampling applicants | Ratio CI, resampling payloads |
|---|---|---|---|---|---|---|---|---|---|---|
| exfil | standard | 480 | 0.56 | 0.01 | 0.006 | 0.004 | 0.71 [0.00–1.78] | 0.09 | [0.00–1.82] | [0.00–1.35] |
| exfil | natural | 480 | 1.00 | 0.05 | 0.052 | 0.050 | 0.96 [0.86–1.00] | nan | [0.87–1.00] | [0.89–1.00] |
| exfil | standard+natural | 960 | 0.78 | 0.03 | 0.024 | 0.027 | 1.11 [0.93–1.26] | 0.09 | [0.91–1.31] | [0.67–1.31] |
| exfil | adaptive | 480 | 1.00 | 0.14 | 0.135 | 0.125 | 0.92 [0.85–0.98] | nan | [0.80–1.00] | [0.82–1.00] |
| integrity | standard | 240 | 0.93 | 0.25 | 0.233 | 0.271 | 1.16 [0.99–1.38] | -0.15 | [0.97–1.43] | [0.97–1.57] |
| integrity | natural | 240 | 1.00 | 0.45 | 0.446 | 0.442 | 0.99 [0.97–1.00] | nan | [0.97–1.00] | [0.97–1.00] |
| integrity | standard+natural | 480 | 0.97 | 0.35 | 0.336 | 0.356 | 1.06 [1.00–1.13] | -0.06 | [0.99–1.13] | [0.99–1.21] |
| integrity | adaptive | 240 | 1.00 | 1.00 | 1.000 | 1.000 | 1.00 [1.00–1.00] | nan | [1.00–1.00] | [1.00–1.00] |

Ratio near 1 = the two layers fail independently (stacking multiplies protection). Ratio well above 1, or phi > 0 = they fail on the same payloads. On the adaptive set the detector miss rate is ~1 by construction, so read the observed stack ASR there, not the ratio.
The bracketed ratio CI resamples applicant and payload pairs. The last two columns resample whole applicants or whole payloads instead.

## Sink filters on model outputs

Exfiltration with no model-based defense (n=1440):

- plain Markdown rendering: 6.5% [5–8]
- simple filter (v0): 0.0% [0–0]
- allowlist filter (safe_render): 0.0% [0–0]


## Post-hoc: escalate instead of drop

Post-hoc analysis (defined after seeing the results). Escalate: if the detector flags any retrieved chunk, the query goes to a human reviewer, assumed to reject it. Computed from the no-defense answers and the recorded detector flags.

| Goal | Payloads | No defense | Detector drops chunk | Detector escalates query | Attacked queries escalated |
|---|---|---|---|---|---|
| integrity | standard | 30.4% [25–37] | 29.6% [24–36] | 20.4% [16–26] | 27.5% [22–33] |
| integrity | natural | 41.2% [35–48] | 41.2% [35–48] | 40.8% [35–47] | 0.4% [0–2] |
| integrity | adaptive | 95.0% [91–97] | 94.6% [91–97] | 93.8% [90–96] | 1.2% [0–4] |
| exfil | standard | 2.9% [2–5] | 0.4% [0–2] | 0.0% [0–1] | 65.8% [61–70] |
| exfil | natural | 5.0% [3–7] | 4.8% [3–7] | 4.8% [3–7] | 0.6% [0–2] |
| exfil | adaptive | 11.7% [9–15] | 10.6% [8–14] | 10.6% [8–14] | 1.9% [1–4] |

Clean queries that would be escalated: 0.0% [0–7].