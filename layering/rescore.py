"""Re-parse the decision and legitimate-link fields of an existing runs.jsonl from the
stored raw outputs. The original file is kept as runs.jsonl.orig.

Usage: python -m layering.rescore --res results_qwen14b
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import shutil

from .defenses import legit_link_kept, plain_render, safe_render
from .pipeline import decision


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    a = ap.parse_args()
    path = os.path.join(a.res, "runs.jsonl")
    if not os.path.exists(path + ".orig"):
        shutil.copy(path, path + ".orig")
    rows = [json.loads(line) for line in open(path)]
    changed = collections.Counter()
    for r in rows:
        new = {"decision": decision(r["output"])}
        if r.get("portfolio_url"):
            new["legit_kept_plain"] = legit_link_kept(plain_render(r["output"]), r["portfolio_url"])
            new["legit_kept_sink"] = legit_link_kept(safe_render(r["output"]), r["portfolio_url"])
        for k, v in new.items():
            if r.get(k) != v:
                changed[(k, r["condition"])] += 1
                r[k] = v
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{a.res}: {len(rows)} rows;",
          "changed fields:", dict(changed) if changed else "none")


if __name__ == "__main__":
    main()
