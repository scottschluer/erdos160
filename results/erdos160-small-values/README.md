# Erdős Problem #160: first exact small values of h(N)

**Problem** ([erdosproblems.com/160](https://www.erdosproblems.com/160)). h(N) is the least k such that {1,…,N} can be
k-coloured so that every 4-term arithmetic progression {a, a+d, a+2d, a+3d} (d ≥ 1) gets at least 3 distinct colours.
Only asymptotic bounds are known, and the page lists no small values (see NOVELTY.md).
Equivalent dual: M(k) = max N with a valid k-colouring. h is non-decreasing, so h(N) = min{k : N ≤ M(k)}.
Equivalently (MathOverflow 410808), the colour classes A_1..A_k partition [N] so that every A_i ∪ A_j is 4-AP-free.

## Claim
| k | M(k) | evidence |
|---|------|----------|
| 3 | **12** | witness + UNSAT at 13 |
| 4 | **22** | witness + UNSAT at 23 |
| 5 | **35** | witness + UNSAT at 36 |
| 6 | **53** | witness + UNSAT at 54: cube-and-conquer, 10067/10067 cubes refuted with LRAT certificates checked by lrat-check (vera); hal's independent run agrees |
| 7 | ≥ 76 | witness (k7_N76.txt; N=73, 74 witnesses also kept); N=74 UNSAT out of reach (see Method) |
| 8 | ≥ 97 | witness (tess, h160ls k=8, ~3 min; stalls at 98) |

Consequently **h(N) is determined exactly for every N ≤ 76**:
h(N) = 1 for N ≤ 3 (no 4-AP), 3 for 4 ≤ N ≤ 12 ({1,2,3,4} already needs 3 colours), 4 for 13 ≤ N ≤ 22,
5 for 23 ≤ N ≤ 35, 6 for 36 ≤ N ≤ 53, and 7 for 54 ≤ N ≤ 76.
(h ≥ 7 on 54..76 because M(6) = 53; h ≤ 7 there because the k=7 witness of length 76 restricts to every shorter prefix.)

Extremal colourings are nearly unique (tess, independently re-counted by vera): up to colour permutation and reversal there are
1 (k=3, N=12), 3 (k=4, N=22) and 5 (k=5, N=35).
All of them are listed in `extremal/` (colours renumbered by first appearance; regenerate with
`.venv/bin/python search/h160_struct/count_extremal.py N K`, an x-only CNF with blocking clauses; vera's re-count is a
plain backtracking DFS, `verify/h160_enum.py`). The unique k=3 colouring 0 0 1 2 1 0 2 1 0 1 2 2 is mapped to itself by
reversal plus a colour swap.

## Files
- `witnesses/k{4,5,6,7,8}_N*.txt`: one line, N space-separated colours (0-based), c(1) first.
- `m6/cubes_N54_k6_block23-32.icnf`: the 10067 cubes for the N=54, k=6 cube-and-conquer (see Method).
- `VERIFICATION.md` (vera), `NOVELTY.md` (remy).

## Method (hal)
- **Lower bounds**: tabu search over colourings (`search/h160/ls.c`). Cost = number of 4-APs with ≤ 2 colours; move =
  recolour one vertex of a random bad AP to its best non-tabu colour; on success extend N by one. It reaches 22 and 35
  instantly and stalls at 23 and 36, so it is calibrated on the known cases. k=6 N=53 takes about 1 s (it never reached 54
  in 3 × 120 s, consistent with M(6)=53); k=7 N=74 took ~550 s, and a warm start from that colouring (`-i`) reached 76.
- **Upper bounds**: SAT. M(3..5) by plain CDCL with value-precedence symmetry breaking. For k=6, N=54, plain kissat and
  march_cu cubes (d=14, ~16k cubes, heavy tail) extrapolate to tens of core-hours. Centre-block cubes are ~15× better:
  every valid colouring of the centre block [23..32] that is a restricted growth string (colours numbered by first
  appearance) and lex ≤ the RGS of its own reversal gives one cube. Any valid colouring of [54] can be mapped to exactly
  such a block by reversing (i → 55−i, which maps the block onto itself) and relabelling colours, so these 10067 cubes
  cover everything, with no other symmetry breaking in the CNF. Generator: `search/h160/block_cubes.py 54 6 23 32`.
  Cube generator sanity check: enumerating all solutions inside every cube recovers exactly 1 / 3 / 5 orbits at
  (k,N) = (3,12), (4,22), (5,35) and 0 at (4,23), (5,36).
- **N=54, k=6 run (hal)**: CNF = `verify/h160_cnf.py 54 6 F.cnf` (vera's direct encoding, no --sb), cubes as assumptions
  to persistent CaDiCaL 1.9.5 instances (pysat), 150-cube chunks, `search/h160/inc_conquer.py`. All 10067 cubes UNSAT,
  13012 CPU-s in total (≈3.6 core-hours), hardest cube 43.8 s. This run produces no proofs; the certificate is vera's
  per-cube LRAT re-solve (VERIFICATION.md).
- **k=7, N=74**: the same construction (block [33..42], 12152 cubes) is not feasible here. In a sample of 8 cubes, 3 were
  refuted immediately and 5 were unresolved after 300 s each, which puts the total at several hundred core-hours or more.

## Re-run
```
# witnesses (lower bounds); search/bin/ is not in git, so build first
mkdir -p search/bin && clang -O3 -o search/bin/h160ls search/h160/ls.c
search/bin/h160ls 6 45 -t 60 -s 2 -o /tmp/h          # k=6 reaches N=53 in ~2 s
search/bin/h160ls 7 74 -i results/erdos160-small-values/witnesses/k7_N74.txt -t 900 -s 21 -o /tmp/h   # 74 -> 76 (run-dependent)
# M(6) = 53 upper bound (uncertified, ~1 h on 4 cores)
.venv/bin/python verify/h160_cnf.py 54 6 F.cnf
.venv/bin/python search/h160/block_cubes.py 54 6 23 32 > cubes.icnf
.venv/bin/python search/h160/inc_conquer.py F.cnf cubes.icnf results.tsv --jobs 4 --chunk 150
# independent checks (vera)
verify/build_deps.sh                                  # drat-trim + lrat-check (pinned) into verify/deps/
verify/run_h160_verification.sh                       # ~50 s: witnesses, M(3..5) certificates, DFS counts
JOBS=7 verify/run_h160_verification.sh --m6           # M(6) certificate, ~3.2 core-hours
```
