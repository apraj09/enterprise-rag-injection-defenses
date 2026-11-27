# Internal Is Not Trusted: code and results

Code, data and results for the article "Internal Is Not Trusted: Choosing Defenses Against Indirect Prompt Injection in Enterprise RAG Assistants".

A synthetic RAG hiring assistant summarizes applicants for a recruiter. Each applicant writes their own resume, which is the attacker's only way in. The attacks try to leak a secret code from the recruiter notes through a rendered link or image (data theft) or to get a weak applicant shortlisted (manipulation). The defenses are Spotlighting with datamarking, the `protectai/deberta-v3-base-prompt-injection-v2` classifier (flagged chunks are dropped) and an output allowlist (`safe_render`), alone and stacked.

## Layout

| Path | Content |
|---|---|
| `layering/data.py` | 60 synthetic applicants (12 dev, 48 test), resumes, recruiter notes, payloads |
| `layering/defenses.py` | Spotlighting, detector, `safe_render`, leak and link measurement |
| `layering/pipeline.py` | retrieval, prompts, model backends (transformers, vLLM, mock) |
| `layering/run.py` | adaptive payload selection on dev applicants, evaluation on test applicants |
| `layering/analyze.py` | `report.md` and `joint_miss.csv` from `runs.jsonl` |
| `layering/sink_tests.py` | 21 sink tricks against a simple filter and `safe_render` |
| `layering/costs.py` | cost of each defense per query |
| `layering/rescore.py` | re-parses decisions in an existing `runs.jsonl` |
| `run_h100.pbs`, `layering/preflight.py` | PBS job used for the runs |
| `results/` | Qwen2.5-7B-Instruct |
| `results_qwen14b/` | Qwen2.5-14B-Instruct |
| `results_phi4/` | Phi-4 |

## Running

Python 3.12. Model runs need a CUDA GPU. All models are ungated on Hugging Face.

```bash
pip install -r requirements.txt

python -m layering.sink_tests
python -m layering.run --backend hf --model Qwen/Qwen2.5-7B-Instruct --out rerun_7b
python -m layering.analyze --res rerun_7b
python -m layering.costs --res rerun_7b --model Qwen/Qwen2.5-7B-Instruct
```

Write reruns to a new folder, as above, so the published results stay unchanged. `sink_tests` needs no GPU, and `python -m layering.run --backend mock --detector mock --out /tmp/mock` checks the harness without one (its numbers mean nothing). Decoding is greedy and answers are cached in `<out>/llm_cache.jsonl`, so an interrupted run resumes. The published runs used the transformers backend (`--backend hf`) and took about 70 min (7B), 155 min (14B) and 163 min (Phi-4) on one H100 MIG slice. `--backend vllm` needs vLLM, which is not in `requirements.txt`.

On a PBS cluster, download the models into `$WORK/hf_cache` on a node with internet access, then submit `run_h100.pbs` as shown at the top of the file.

Model snapshots: Qwen2.5-7B-Instruct `a09a35458c702b33eeacc393d103063234e8bc28` and deberta-v3-base-prompt-injection-v2 `90c9989b1a342275dd0d1a95aad283c04e075671`. Qwen2.5-14B-Instruct and Phi-4 were taken from the main branch in November 2026.

## Results

Each results folder holds `runs.jsonl` (one row per applicant, payload and condition, with the raw answer and every measured field), `report.md` (attack success with 95% Wilson intervals for every payload set, clean-query utility, the correlated-failure test, sink filters and the escalation analysis), `joint_miss.csv`, `payloads.json`, `adaptive_selection.json`, `costs.md`, `costs.json` and `meta.json`. In the files, data theft is `exfil`, manipulation is `integrity` and crude payloads are `standard`.

Each run has 8,832 answers: 48 test applicants × 30 theft payloads, 24 weak applicants × 30 manipulation payloads and 48 clean queries, each under the four model conditions `none`, `spot`, `det` and `spot_det`. The allowlist rows filter these same answers, so they need no extra model calls.

Natural payloads are random combinations of the hand-written templates in `layering/data.py` (10 framings and 8 bodies per goal, with hosts and placements). Adaptive payloads come from the same templates and are selected separately for each model on its 12 dev applicants. `leak_plain_loose` and `leak_sink_loose` also count percent-encoded, base64-encoded and reformatted copies of the secret.

Five of the 21 sink tricks come from disclosed incidents: the reference-style image, the reference-style link and the Microsoft Teams proxy from EchoLeak ([Reddy and Gujral, 2025](https://arxiv.org/abs/2509.10540)), the Markdown link from Slack AI ([PromptArmor, 2024](https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via)) and the Apps Script host from Google Bard ([Rehberger, 2023](https://embracethered.com/blog/posts/2023/google-bard-data-exfiltration/)). The other 16 are common HTML variants.

| Number in the article | Source |
|---|---|
| Table 2 | `results/report.md`, attack success table and the legit links column of the clean-query table |
| 34 legitimate links, 15 on the company host and 19 on GitHub | `portfolio_url` of the clean rows in `runs.jsonl` |
| Correlation between the two layers' failures below 0.05 | `joint_miss.csv`, column `phi` |
| None of the 48 clean resumes flagged | `report.md`, last line |
| Detector flags 18.8% of payloads, payload text still reaches the model in 44% of flagged cases | `results/report.md`, below the attack success table |
| Observed/predicted 1.02 and 1.14 (7B), 1.08 (14B), 1.06 (Phi-4) | `joint_miss.csv` of each model, rows `standard+natural` |
| Adaptive manipulation with all three defenses, 64.2% (14B) and 100% (Phi-4) | `report.md` of those models, row `All three` |
| Escalate instead of drop | `report.md`, last section |
| Costs | `costs.md` |
| Simple filter leaks on 9 of 21 tricks | `python -m layering.sink_tests` |
| Detector flags 66% of crude theft payloads and under 4% of the others | `poison_flagged`, condition `none`, exfil rows by payload set |
| 132, 178 and 351 of 5,760 theft attempts leak, none after the allowlist | `leak_plain` and `leak_sink`, exfil rows of the four model conditions |
| 62 of 1,440 undefended answers contain an attacker link | exfil rows of condition `none` with a link to `EXFIL_HOST_STD` or `NATURAL_HOSTS` from `layering/data.py` |
| All 20 new successes with the detector come from partial deletion | integrity `standard` rows, `det` against `none`, `poison_flagged` and `poison_survives` |
| The 14B model copies the marker into 58% of its answers | condition `spot` in `results_qwen14b/runs.jsonl`, answers containing `ˆ` |

## Notes

- Qwen2.5-14B-Instruct and Phi-4 were chosen before any of their results were seen.
- Reading raw answers after the 14B run showed that the decision parser missed two formats, the datamark copied into `DECISION:ˆSHORTLIST` and `**Decision**: SHORTLIST`. The parser was fixed, the link check was made to ignore punctuation right after a plain-text URL, and all three runs were re-parsed from the stored answers with `layering/rescore.py`. The original files are kept as `runs.jsonl.orig`. No model answer changed, and the 7B results did not change.
- The escalation analysis was defined after seeing the detector results. It uses only the recorded answers and detector flags.
