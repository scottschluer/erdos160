# Independent verification: Erdős #160 small values (vera, 2026-10-18)

**Verdict:** M(3)=12, M(4)=22 and M(5)=35 are each **VERIFIED** three independent ways. **M(6)=53 is VERIFIED** by a
checked LRAT certificate (section 4). The lower bounds M(7) ≥ 76 (earlier ≥ 73, ≥ 74) and M(8) ≥ 97 are **VERIFIED**
(witness colourings check out). M(7) and M(8) are lower bounds only, with no upper-bound certificate.
Consequently h(N) is exact for every N ≤ 76. For 54 ≤ N ≤ 76, M(6) = 53 < N gives h(N) ≥ 7, and the N=76 witness
restricted to [1..N] gives h(N) ≤ 7. h(77) is open (7 or 8).

## Definition checked against
erdosproblems.com/160 and the formal statement `Erdos160.erdos_160.h` (google-deepmind/formal-conjectures,
`ErdosProblems/160.lean`): h(N) = least k such that some colouring {1..N} → Fin k gives every 4-term AP at least 3
distinct colours. In the formal statement a 4-AP is a set with `ENat.card = 4` of the form {a + n·d : n < 4}, so d ≥ 1.
That is the same object all my checkers use: {a, a+d, a+2d, a+3d} ⊆ [1, N], d ≥ 1.
M(k) := max N with a valid k-colouring of [1..N]. h is non-decreasing because restricting a valid colouring to a prefix keeps it valid. So M(k) = N
⇔ (a valid k-colouring of [N] exists) ∧ (no valid k-colouring of [N+1] exists).

## Independence
None of my tools import or read anything from `search/`. The encoder, checker and enumerator were written from the definition above:
- `verify/h160_coloring.py`: witness checker. A direct (a, d) loop and a numpy pass must agree.
- `verify/h160_cnf.py`: my own CNF. One-hot x(i,c), ALO + AMO, a long clause per (4-AP, colour pair), and
  value-precedence symmetry breaking (soundness argument in the file header). There are no auxiliary variables, so it differs from hal's
  y-variable encoding. The solver is CaDiCaL 3.0.1, not hal's kissat.
- `verify/h160_enum.py`: exhaustive backtracking with value precedence. No SAT involved.
- Tests (`verify/test_h160.py`): the CNF agrees with brute force over all k^N colourings for k=2 (N≤8) and k=3 (N≤13), with
  and without SB. Both checker methods agree on 500 random colourings.

## Re-run
```
verify/run_h160_verification.sh        # ~50 s; needs .venv, cadical on PATH, network+clang on first run
                                       # (verify/build_deps.sh fetches drat-trim @2e3b2dc into verify/deps/)
JOBS=7 verify/run_h160_verification.sh --m6    # adds section 4, the M(6) certificate (~3.2 core-hours)
```

## Output (2026-10-18)
```
== 1. witness colourings (lower bounds M(k) >= N)        [hal's files in witnesses/]
-- k4_N22.txt   4-APs: 70 checked    VERDICT: VALID colouring of [1..22] with 4 colours => M(4) >= 22
-- k5_N35.txt   4-APs: 187 checked   VERDICT: VALID colouring of [1..35] with 5 colours => M(5) >= 35
-- k6_N53.txt   4-APs: 442 checked   VERDICT: VALID colouring of [1..53] with 6 colours => M(6) >= 53
-- k7_N73.txt   4-APs: 852 checked   VERDICT: VALID colouring of [1..73] with 7 colours => M(7) >= 73
-- k7_N74.txt   4-APs: 876 checked   VERDICT: VALID colouring of [1..74] with 7 colours => M(7) >= 74   (hal, later)
-- k7_N76.txt   4-APs: 925 checked   VERDICT: VALID colouring of [1..76] with 7 colours => M(7) >= 76   (hal, later)
-- k8_N97.txt   4-APs: 1520 checked  VERDICT: VALID colouring of [1..97] with 8 colours => M(8) >= 97   (tess)
== 2. UNSAT at N = M(k)+1 (upper bounds), own encoding, cadical + DRAT
-- k=3 N=13: s UNSATISFIABLE   drat-trim: s VERIFIED (68 of 144 clauses in core)      lrat-check: c VERIFIED
-- k=4 N=23: s UNSATISFIABLE   drat-trim: s VERIFIED (469 of 692 clauses in core)     lrat-check: c VERIFIED
-- k=5 N=36: s UNSATISFIABLE   drat-trim: s VERIFIED (2039 of 2520 clauses in core)   lrat-check: c VERIFIED
== 3. exhaustive backtracking (no SAT)
N=12 k=3: 1 colourings up to colour permutation; 1 up to permutation+reversal
N=13 k=3: 0
N=22 k=4: 6 up to permutation; 3 up to permutation+reversal
N=23 k=4: 0
N=35 k=5: 10 up to permutation; 5 up to permutation+reversal
N=36 k=5: 0
```
Full unabridged output: `vera_verify.log` in this folder. Note: drat-trim prints `\n\rs VERIFIED`, so a plain
`grep '^s '` misses the verdict line. The script strips `\r` first. An earlier draft of this file was written before
I noticed that; the log has since been regenerated and contains all 3 `s VERIFIED` and 3 `c VERIFIED` lines.
M(3)=12 was also confirmed by a numpy brute force over all 3^12 and 3^13 colourings (`test_h160.py`).

## 4. M(6) = 53: no valid 6-colouring of [1..54]
**Method (centre-block cube-and-conquer, hal's idea, re-implemented independently).** Let F = `h160_cnf.py 54 6` with **no**
symmetry breaking, so every valid colouring satisfies F. Let G = S6 × ⟨ρ⟩, where ρ(i) = 55 − i. G acts on valid colourings
of [54] and preserves validity. The block [23..32] is ρ-invariant, so restriction to the block commutes with G. For each
G-orbit of valid block colourings, take the representative r = min(RGS(b), RGS(reverse b)) (RGS = colours renumbered by
first use). Then any valid colouring c of [54] has some g ∈ G with g·c restricted to the block equal to a representative r. So F is UNSAT
iff F ∧ (block = r) is UNSAT for every r. Block colourings that are invalid inside the block cannot extend, so they are
not needed. This is a hand proof. The two controls below test the code that implements it.

**Run.**
```
.venv/bin/python verify/h160_cnf.py 54 6 F54_6_nosb.cnf          # 324 vars, 7749 clauses (sha256 7ef191c4…)
.venv/bin/python verify/h160_blockcubes.py 54 6 23 32 cubes.icnf --compare m6/cubes_N54_k6_block23-32.icnf
  block [23..32] (length 10), K=6: 19919 valid block colourings up to S_K, 10067 up to S_K x reversal
  compare: mine 10067, theirs 10067, missing from theirs 0, extra in theirs 0      (files byte-identical, sha256 6961e9fe…)
.venv/bin/python verify/cnc_check.py F54_6_nosb.cnf cubes.icnf --lrat --no-coverage --jobs 7 --log cert.log
  coverage: NOT CHECKED HERE (--no-coverage; must be argued separately)      <- the orbit argument above
  VERDICT: VERIFIED — all 10067 cubes UNSAT with checked LRAT (coverage argued separately)
  log audit: 10067 distinct cube indices OK, 0 FAIL; 11572 cube-seconds total, hardest cube 26.1 s
```
Each cube was solved with `cadical --lrat` on F plus the cube's 10 unit clauses, and the proof was checked by
`lrat-check`. Per-cube log: `m6/vera_cert_lrat.log`. The run was restarted once (4 → 7 workers) and resumed from the log;
only cubes with a completed lrat-check are logged OK.
The cube generator is my backtracking enumerator (`h160_enum.py`, no SAT). hal generated his cube file with separate code,
`search/h160/block_cubes.py`, and the two files are identical.

**Controls run through the same pipeline:** N=36, k=5 with block [14..23] (4991 cubes) gives all VERIFIED, as M(5)=35
requires. N=35, k=5 with block [17..19] (4 cubes) gives `NOT VERIFIED — 1 cube(s) failed: [3]`, so a satisfiable
cube is caught.

## Attacks tried
- **Definition drift:** I compared against the formal Lean statement as well as the prose. d ≥ 1 is forced by card = 4, and every AP is
  taken as a set, so direction doesn't matter. The MathOverflow reformulation (A_i ∪ A_j has no 4-AP) is equivalent.
- **Encoding cheats:** without AMO the direct encoding is trivially SAT (all-true). This was caught in testing and AMO is now mandatory.
  The brute-force agreement covers this bug class.
- **Symmetry-breaking soundness:** only value precedence is used, and relabelling colours by first use maps any valid colouring
  to one that satisfies it. The DFS enumerator applies the same precedence, but it is a separate implementation with no CNF.
- **Extremal-structure claim (tess, m51):** independently reproduced. k=3: 1 class, k=4: 3, k=5: 5 up to permutation+reversal.
- **M(6) coverage:** the cube set is symmetry-reduced, so a plain "negated cubes are UNSAT" tautology check would be wrong.
  It is replaced by the orbit argument, plus an independent re-generation of the cube set that matches hal's byte for byte.
  The cube literals are the positive x(i,c). AMO in F forces the other colours of each block vertex false.
- **Not attacked:** M(7), M(8) upper bounds. No certificate exists, and hal estimates several hundred core-hours for k=7.
