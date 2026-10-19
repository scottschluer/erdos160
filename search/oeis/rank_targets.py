"""Rank cached OEIS JSON results as extension targets: few terms, stale edits, combinatorial wording."""
import json, sys, glob, re

seen = {}
for f in sys.argv[1:]:
    try:
        data = json.load(open(f))
    except Exception:
        continue
    for s in data or []:
        seen[s["number"]] = s

GOOD = re.compile(r"graph|polyomino|permutation|matri|maximal|maximum|minimum|board|queens|knight|tournament|lattice|tiling|sets? of|subsets|colorings|n X n|words|necklace|ruler|design|code|square", re.I)
BAD = re.compile(r"prime|digit|decimal|repunit|factorial\(|continued fraction|base \d|palindrom|busy beaver|Ramsey|pseudoprime|Fermat|Mersenne|aliquot|sigma|phi\(", re.I)
rows = []
for n, s in seen.items():
    terms = s.get("data", "").split(",")
    name = s.get("name", "")
    kw = s.get("keyword", "")
    if "more" not in kw or BAD.search(name):
        continue
    if not GOOD.search(name):
        continue
    yr = int(s.get("time", "0000")[:4])
    rows.append((len(terms), yr, n, kw, name[:150], terms[-3:]))
rows.sort(key=lambda r: (r[0], r[1]))
for r in rows:
    print(f"A{r[2]:06d} nt={r[0]:3d} last={r[1]} [{r[3]}] {r[4]} | tail={','.join(r[5])}")
print(len(seen), "unique sequences;", len(rows), "after filter", file=sys.stderr)
