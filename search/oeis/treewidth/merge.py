"""Merge geng_tw part logs in a directory: sum TWE cells, TW totals, and TWINFO counters; write summary.json."""
import json, re, sys, glob, os
from collections import defaultdict
d = sys.argv[1]
cells = defaultdict(int); tot = defaultdict(int); info = defaultdict(float); over = 0; n = None; parts = 0
for f in sorted(glob.glob(os.path.join(d, "part*.log"))):
    parts += 1
    for line in open(f):
        w = line.split()
        if not w: continue
        if w[0] == "TWE": n = int(w[1]); cells[(int(w[2]), int(w[3]))] += int(w[4])
        elif w[0] == "TW": tot[int(w[2])] += int(w[3])
        elif w[0] == "TWOVERCAP": over += int(w[3])
        elif w[0] == "TWINFO":
            kv = dict(x.split("=") for x in w[1:])
            for k in ("nout", "prune_calls", "mismatches", "cpu"): info[k] += float(kv[k])
            if kv["K"] != "-2":  # parts that produced no graphs never read the environment
                info["K"] = kv["K"]; info["DEC"] = kv["DEC"]; info["CHECK"] = kv["CHECK"]; info["CAP"] = kv["CAP"]
assert sum(cells.values()) == sum(tot.values()), "TWE/TW totals disagree"
summary = {"n": n, "parts": parts, "tw_counts": {str(k): tot[k] for k in sorted(tot)}, "over_cap": over,
           "total": sum(tot.values()) + over,
           "info": {k: (int(v) if isinstance(v, float) and k != "cpu" else v) for k, v in info.items()},
           "cells_tw_edges": {f"{t},{e}": c for (t, e), c in sorted(cells.items())}}
json.dump(summary, open(os.path.join(d, "summary.json"), "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("n", "parts", "tw_counts", "over_cap", "total", "info")}))
