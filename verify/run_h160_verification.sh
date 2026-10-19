#!/bin/sh
# Re-run vera's independent verification of Erdős #160 small values.
#   verify/run_h160_verification.sh [WORKDIR]            ~1 min
#   verify/run_h160_verification.sh --m6 [WORKDIR]       also the M(6)=53 certificate (~4 core-hours; JOBS=4)
# Needs: .venv (numpy, numba, pysat), cadical, drat-trim + lrat-check
# (DRAT_TRIM / LRAT_CHECK env vars; default: verify/deps/drat-trim, built by verify/build_deps.sh).
set -e
M6=0
if [ "$1" = "--m6" ]; then M6=1; shift; fi
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PY="$ROOT/.venv/bin/python"
W=${1:-$ROOT/scratch/h160_verify}
[ -n "$DRAT_TRIM" ] && [ -n "$LRAT_CHECK" ] || "$ROOT/verify/build_deps.sh" > /dev/null
DRAT_TRIM=${DRAT_TRIM:-$ROOT/verify/deps/drat-trim/drat-trim}
LRAT_CHECK=${LRAT_CHECK:-$ROOT/verify/deps/drat-trim/lrat-check}
export DRAT_TRIM LRAT_CHECK
RES="$ROOT/results/erdos160-small-values"
mkdir -p "$W"

echo "== 1. witness colourings (lower bounds M(k) >= N)"
for f in "$RES"/witnesses/k*_N*.txt; do
    k=$(basename "$f" | sed -E 's/^k([0-9]+)_N.*/\1/')
    echo "-- $(basename "$f")"
    "$PY" "$ROOT/verify/h160_coloring.py" "$f" --k "$k" | grep -E '^(N |colours|4-APs|VERDICT)'
done

echo "== 2. UNSAT at N = M(k)+1 (upper bounds), own encoding, cadical + DRAT"
for kn in 3:13 4:23 5:36; do
    k=${kn%%:*}; N=${kn#*:}
    cnf="$W/v_N${N}_k${k}_sb.cnf"
    "$PY" "$ROOT/verify/h160_cnf.py" "$N" "$k" "$cnf" --sb
    set +e
    cadical -q --no-binary "$cnf" "$W/v_N${N}_k${k}.drat" > "$W/v_N${N}_k${k}.out"
    set -e
    echo "-- k=$k N=$N: $(grep '^s' "$W/v_N${N}_k${k}.out")"
    "$DRAT_TRIM" "$cnf" "$W/v_N${N}_k${k}.drat" -L "$W/v_N${N}_k${k}.lrat" | tr -d "\r" | grep -E '^s |in core'
    echo "   lrat-check: $("$LRAT_CHECK" "$cnf" "$W/v_N${N}_k${k}.lrat" | grep -E 'VERIFIED|FAIL' | head -1)"
done

echo "== 3. exhaustive backtracking (no SAT): counts at N=M(k), zero at N=M(k)+1"
for kn in 3:12 3:13 4:22 4:23 5:35 5:36; do
    "$PY" "$ROOT/verify/h160_enum.py" "${kn#*:}" "${kn%%:*}"
done

if [ $M6 = 1 ]; then
    echo "== 4. M(6) = 53: N=54, k=6 UNSAT by centre-block cubes (own CNF without SB, own cubes, LRAT per cube)"
    "$PY" "$ROOT/verify/h160_cnf.py" 54 6 "$W/F54_6_nosb.cnf"
    "$PY" "$ROOT/verify/h160_blockcubes.py" 54 6 23 32 "$W/cubes54.icnf" \
        --compare "$RES/m6/cubes_N54_k6_block23-32.icnf"
    "$PY" "$ROOT/verify/cnc_check.py" "$W/F54_6_nosb.cnf" "$W/cubes54.icnf" --lrat --no-coverage \
        --jobs "${JOBS:-4}" --work "$W/m6work" --log "$W/m6cert.log" | grep -E "cubes:|coverage|VERDICT"
fi
