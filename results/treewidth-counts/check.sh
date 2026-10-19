#!/bin/sh
# Re-check the treewidth claims from scratch.
#   results/treewidth-counts/check.sh          quick: build, brute force n<=11, GF to n=100, compare (~3 min on 4 cores)
#   results/treewidth-counts/check.sh --full   also n=12 tw<=3 and n=13 tw<=2 (~45 CPU-min)
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"
PY="$ROOT/.venv/bin/python -I"
T=search/oeis/treewidth
W=$(mktemp -d /tmp/twcheck.XXXXXX)
$T/build.sh > /dev/null
$T/run.sh 10 4 "$W/n10_all" TWCHECK=1 > /dev/null
GENGBIN=geng_twpp $T/run.sh 11 4 "$W/n11_K3" TWK=3 TWCHECK=1 > /dev/null
if [ "$1" = "--full" ]; then
  GENGBIN=geng_twpp $T/run.sh 12 4 "$W/n12_K3" TWK=3 > /dev/null
  GENGBIN=geng_twpp $T/run.sh 13 4 "$W/n13_K2" TWK=2 > /dev/null
fi
$PY $T/sp_gf.py 100 > "$W/gf.txt"
$PY - "$W" "$ROOT/results/treewidth-counts" <<'EOF'
import json, glob, sys, os
W, R = sys.argv[1], sys.argv[2]
claims = json.load(open(os.path.join(R, "claims.json")))
ok = True
def check(label, got, want):
    global ok
    flag = "OK" if got == want else "MISMATCH"
    ok &= got == want
    print(f"{flag:8s} {label}: computed {got} claimed {want}")
row10 = json.load(open(f"{W}/n10_all/summary.json"))["tw_counts"]
check("A263294 row 10", [row10[str(k)] for k in range(10)], claims["A263294"]["10"])
for d in glob.glob(f"{W}/n1[1-3]_K*"):
    s = json.load(open(d + "/summary.json")); n = str(s["n"]); tc = s["tw_counts"]
    if "2" in tc and n in claims["A362908"]: check(f"A362908({n}) brute", tc["2"], claims["A362908"][n])
    if "3" in tc and n in claims["A362907"]: check(f"A362907({n}) brute", tc["3"], claims["A362907"][n])
    assert s["info"]["mismatches"] == 0
gf = {int(l.split()[0]): int(l.split()[5]) for l in list(open(f"{W}/gf.txt"))[1:]}
b = {int(l.split()[0]): int(l.split()[1]) for l in open(os.path.join(R, "gf/b362908.txt"))}
check("A362908 GF n=1..100 vs gf/b362908.txt", all(gf[n] == b[n] for n in range(1, 101)), True)
for n, v in claims["A362908"].items():
    check(f"A362908({n}) GF", gf[int(n)], v)
print("ALL OK" if ok else "FAILURES")
sys.exit(0 if ok else 1)
EOF
