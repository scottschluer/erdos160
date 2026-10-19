#!/bin/sh
# vera's independent re-check of results/treewidth-counts/claims.json.
# Uses only verify/ code (own geng hooks, own deciders, own GF).
#   verify/treewidth/run_verification.sh          quick: n<=11 pruned, row 10, GF to 100 (~5 CPU-min)
#   verify/treewidth/run_verification.sh --full   also n=12 tw<=3, n=13 tw<=2, row 11 (~3 CPU-h)
# Needs NAUTY=<configured nauty2_9_3 tree> (see build.sh).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
PY="$ROOT/.venv/bin/python"
B="$HERE/bin"
W=$(mktemp -d /tmp/vera_twverify.XXXXXX)
"$HERE/build.sh" > /dev/null
"$HERE/test.sh" | tail -1
par() {  # n parts env... -> summed histogram "out h0 h1 ..."
    n=$1; p=$2; shift 2
    i=0
    while [ $i -lt "$p" ]; do
        env "$@" "$B/vgeng" -q "$n" $i/"$p" 2> "$W/n${n}_${i}_$$.log" > /dev/null &
        i=$((i + 1))
    done
    wait
    cat "$W"/n${n}_*_$$.log | grep '^VERA' > "$W/last.txt"
    "$PY" - "$W/last.txt" <<'EOF'
import sys, re
tot = None; out = 0
for l in open(sys.argv[1]):
    m = re.search(r'out=(\d+) .*mismatches=(\d+) hist: (.*)', l)
    assert m and m.group(2) == '0', l
    h = list(map(int, m.group(3).split())); out += int(m.group(1))
    tot = h if tot is None else [a + b for a, b in zip(tot, h)]
print(out, *tot)
EOF
    rm -f "$W"/n${n}_*_$$.log
}
{
    echo "row10      $(par 10 4)"
    echo "n11 k2 sp  $(par 11 4 VERA_K=2 VERA_DEC=sp)"
    echo "n11 k2 el  $(par 11 4 VERA_K=2 VERA_DEC=elim)"
    echo "n11 k3 ap  $(par 11 4 VERA_K=3 VERA_DEC=ap)"
    if [ "$1" = "--full" ]; then
        echo "n12 k3 ap  $(par 12 4 VERA_K=3 VERA_DEC=ap)"
        echo "n13 k2 sp  $(par 13 4 VERA_K=2 VERA_DEC=sp)"
        echo "row11      $(par 11 4)"
    fi
} > "$W/brute.txt"
cat "$W/brute.txt"
"$PY" "$HERE/sp_gf_vera.py" 100 --check > "$W/gf.txt"
"$PY" - "$W" "$ROOT/results/treewidth-counts" <<'EOF'
import json, os, sys
W, R = sys.argv[1], sys.argv[2]
claims = json.load(open(os.path.join(R, "claims.json")))
ok = True
def check(label, got, want):
    global ok
    ok &= got == want
    print(f"{'OK' if got == want else 'MISMATCH':8s} {label}: vera {got} claimed {want}")
br = {}
for l in open(f"{W}/brute.txt"):
    lab, rest = l[:10].strip(), list(map(int, l[10:].split()))
    br[lab] = rest[1:]                     # drop output count
n_of = {"row10": 10, "row11": 11}
for lab, h in br.items():
    if lab.startswith("row"):
        n = n_of[lab]
        if str(n) in claims.get("A263294", {}):
            check(f"A263294 row {n}", h[:n], claims["A263294"][str(n)])
        for k, seq in ((2, "A362908"), (3, "A362907")):
            if str(n) in claims[seq]:
                check(f"{seq}({n}) unpruned", h[k], claims[seq][str(n)])
    else:
        n, k = int(lab[1:3]), int(lab[5])
        seq = "A362908" if k == 2 else "A362907"
        if str(n) in claims[seq]:
            check(f"{seq}({n}) pruned {lab[7:]}", h[k], claims[seq][str(n)])
        if k == 3 and str(n) in claims["A362908"]:
            check(f"A362908({n}) from k=3 run", h[2], claims["A362908"][str(n)])
gf = {}
for l in open(f"{W}/gf.txt"):
    s = l.split()
    if s and s[0].isdigit():
        gf[int(s[0])] = int(s[4])
for n, v in claims["A362908"].items():
    check(f"A362908({n}) vera GF", gf[int(n)], v)
bf = os.path.join(R, "gf/b362908.txt")
if os.path.exists(bf):
    b = {int(l.split()[0]): int(l.split()[1]) for l in open(bf) if l.strip()}
    check("gf/b362908.txt n=1..100 vs vera GF", all(gf[n] == b[n] for n in range(1, 101)), True)
print("ALL OK" if ok else "FAILURES")
sys.exit(0 if ok else 1)
EOF
