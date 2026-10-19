"""Offline filter over OEIS stripped+names: short sequences whose names match a regex."""
import gzip, re, sys
pat = re.compile(sys.argv[1], re.I)
lo, hi = int(sys.argv[2]), int(sys.argv[3])
names = {}
with gzip.open("/tmp/oeis_full/names.gz", "rt") as f:
    for line in f:
        if line.startswith("A"):
            a, nm = line.rstrip("\n").split(" ", 1)
            names[a] = nm
with gzip.open("/tmp/oeis_full/stripped.gz", "rt") as f:
    for line in f:
        if not line.startswith("A"):
            continue
        a, d = line.split(" ", 1)
        terms = d.strip().strip(",").split(",")
        nm = names.get(a, "")
        if lo <= len(terms) <= hi and pat.search(nm):
            print(f"{a} nt={len(terms):2d} {nm[:170]} | last={terms[-1][:25]}")
