# Independent verification: unlabeled graphs counted by treewidth (vera, 2026-10-18)

**Verdict (so far):** every new value below was recomputed blind with independent code and matches dara's numbers exactly.

| claim | dara | vera | status |
|---|---|---|---|
| A263294 row n=10 | 1, 328, 56756, 1292868, 5502502, 4574482, 570499, 7690, 41, 1 | same | **VERIFIED** |
| A263294 row n=11 | 1, 709, 374887, 22230001, 236650986, 532355501, 217202772, 10149899, 33052, 55, 1 | same | **VERIFIED** |
| A362908 (tw=2) a(10) | 56756 | 56756 | **VERIFIED** |
| A362908 a(11) | 374887 | 374887 | **VERIFIED** |
| A362908 a(12) | 2607705 | 2607705 | **VERIFIED** |
| A362907 (tw=3) a(10) | 1292868 | 1292868 | **VERIFIED** |
| A362907 a(11) | 22230001 | 22230001 | **VERIFIED** |
| A362907 a(12) | 404312886 | 404312886 | **VERIFIED** |
| A362908 a(13) | 18828907 | 18828907 (brute force, 2 pruners) | **VERIFIED** |
| A362908 a(14) | 139869316 | 139869316 (my brute force + my GF) | **VERIFIED** |
| A362908 a(15..100) and connected / all K4-minor-free counts n ≤ 100 (gf/*.txt) | dara's GF | my independent GF | **VERIFIED** (two implementations agree, 0 mismatches in 600 values) |

"Blind" means each side posted its own number before seeing the other's (room log m42/m49 for n=10,11; m59/m61 for n=12;
m85/m86 for row 11).
For n=13 the GF prediction was public before my brute force finished, but the brute force is not tunable: its output is an exact count.
Later rows and terms will be added here as they are checked.

## Definition checked against
A263294: T(n,k) = number of unlabeled simple graphs on n vertices with treewidth exactly k, rows n ≥ 1, k = 0..n−1
(offset 1). A362908 / A362907 are its columns k=2 / k=3 with offset 0, so a(10) is the 11th term. The OEIS programs
use Sage `g.treewidth()` over `graphs(n)`, i.e. standard treewidth over all (not necessarily connected) graphs. This matches
what I count. tw(K_1) = 0 and the edgeless graph has tw 0, which is consistent with T(n,0) = 1.

## Independence
My code is in `verify/treewidth/` and was written without reading `search/`:
- **Generation:** my own build of nauty 2.9.3 `geng`. The tarball sha256 is in `build.sh`. It was downloaded separately from dara's
  copy and the checksums match. The hooks are mine (`vgeng_hook.c`).
- **Exact treewidth:** an elimination game on the fill graph. tw ≤ k iff vertices can be eliminated one at a time, each
  with ≤ k current neighbours, where eliminating v makes N(v) a clique. The search is a DFS memoised on the eliminated set,
  with a simplicial-vertex forced move and a degeneracy cut. tw = the least such k, starting from degeneracy. dara uses the
  Q-set formulation, which is equivalent in theory but is different code, and it never builds a fill graph.
- **Pruning deciders (k=2, k=3):** series-parallel reduction for tw ≤ 2, and the **Arnborg–Proskurowski** reduction
  rules (degree ≤ 1, series, triangle, buddy, cube) for tw ≤ 3. These are search-free and algorithmically unrelated to
  the elimination game. Each rule is safe, because the reduced graph is a minor and tw(G) ≤ max(3, tw(G')). Completeness (some rule
  always applies to a nonempty partial 3-tree) is the AP theorem, and the cross-checks below confirm it empirically for n ≤ 12.
- **Generating function (tw ≤ 2, any n):** `sp_gf_vera.py`, written only from dara's prose spec `GF.md`. I re-derived each
  equation before coding (twisted chains, dihedral cycle index, bond with E₂ᵗ = (S_t² + S(x²))/2, bipartite SPQR
  dissymmetry B₂ = B_S + B_P − B_SP, block-cut dissymmetry). I never read `search/oeis/treewidth/sp_gf.py`.
- **Cross-checks on every output graph:** OUTPROC computes exact tw and also runs both reduction deciders. A
  disagreement increments `mismatches`, and every run reported 0.

## Re-run (cold-tested from a fresh clone, 2026-10-18)
```
verify/treewidth/run_verification.sh          # ~80 s wall: build (fetches sha256-pinned nauty 2.9.3 via
                                              # verify/build_deps.sh), self-tests, n<=11 brute force, GF to 100,
                                              # compare with claims.json and gf/b362908.txt -> "ALL OK"
verify/treewidth/run_verification.sh --full   # adds n=12 tw<=3, n=13 tw<=2, row 11 (~3 CPU-hours)
```

## Self-tests
`verify/treewidth/build.sh && verify/treewidth/test.sh` reproduces OEIS A263294 rows n = 1..9 exactly with unpruned
generation, and the tw ≤ 2 and tw ≤ 3 partial rows with every pruner (elim/sp for k=2, elim/ap for k=3). It also
checks hand-made graphs: K4 → 3, C5 → 2, K5 → 4, octahedron → 4, P4 → 1, edgeless → 0 (decoded with `showg`).

## Runs and output
All runs use `B=verify/treewidth/bin`; `res/mod` splits are summed.
```
# row n=10, unpruned, 4 parts                      (twtool on geng -q 10 r/4; same deciders)
n=10 row: 1 328 56756 1292868 5502502 4574482 570499 7690 41 1   sum 12005168 = A000088(10)   mismatches 0

# n=11, tw<=2: two different pruners, identical output
VERA_K=2 VERA_DEC=sp   $B/vgeng -q 11   -> out=375597 hist: 1 709 374887      mismatches=0
VERA_K=2 VERA_DEC=elim $B/vgeng -q 11   -> out=375597 hist: 1 709 374887      mismatches=0

# n=11, tw<=3: AP pruner and elimination pruner, each in 2 parts, identical per part
dec=ap   0/2: out=11368303 hist: 1 462 251319 11116521 ; 1/2: out=11237295 hist: 0 247 123568 11113480
dec=elim 0/2: out=11368303 hist: 1 462 251319 11116521 ; 1/2: out=11237295 hist: 0 247 123568 11113480
  => tw2(11) = 374887, tw3(11) = 22230001, tw<=3 total 22605598

# n=12, tw<=2 (SP pruner, 2 parts): hist 1+0, 674+926, 1187053+1420652      => tw2(12) = 2607705
# n=12, tw<=3 (AP pruner, 4 parts, 2139 s CPU): total 406922192 = 1 + 1600 + 2607705 + 404312886
  => tw3(12) = 404312886, mismatches 0 in all parts

# n=13, tw<=2: SP pruner and elimination pruner, each in 2 parts, identical per part
dec=sp   0/2: out=10129816 hist: 0 1203 10128613 ; 1/2: out=8702749 hist: 1 2454 8700294
dec=elim 0/2: out=10129816 hist: 0 1203 10128613 ; 1/2: out=8702749 hist: 1 2454 8700294
  => tw2(13) = 18828907, tw<=2 total 18832565 (= GF), tw1 = 3657 = A005195(13) - 1

# row n=11, unpruned, all graphs, 4 parts (1724 s CPU):  $B/vgeng -q 11 r/4
row 11: 1 709 374887 22230001 236650986 532355501 217202772 10149899 33052 55 1
  sum 1018997864 = A000088(11); T(11,1) = 709 = A005195(11)-1; T(11,9) = 55 = p(11)-1; mismatches 0
  tw2, tw3 entries equal the pruned runs above (which used different deciders)

# n=14, tw<=2 (SP pruner, 4 parts, 17452 s CPU, 0 mismatches)
hist sums: tw0 = 1, tw1 = 8598 = A005195(14)-1, tw2 = 45687379+33600613+44227273+16354051 = 139869316
  => tw2(14) = 139869316; tw<=2 total 139877915 = GF all(14). Matches dara's brute force and both GFs.

# GF, n <= 100 (90 s):  .venv/bin/python verify/treewidth/sp_gf_vera.py 100 --check
check: block-cut composition with B=K2 reproduces Otter forests [1, 1, 2, 3, 6, 10, 20, 37, 76, 153, 329, 710]
blocks (g = x), n=1..: 0 1 1 2 5 15 51 230 1142 6369 37601 232259 1476120 9599522 ...
  -> n=1..12 equal brute force (A362908, connected and all tw<=2); n=13 equals my brute force
  -> diff vs dara's gf/{all_tw_le2,connected_tw_le2,forests,b362908,blocks,tw_eq2}.txt, n=1..100: 0 mismatches each
```
Full GF output: `vera_logs/gf_vera_100.txt`. Independent external anchors for the GF: (a) the block column equals
Giménez–Noy–Rué arXiv:0712.1869 eq. (108) through n=14 (found by remy); (b) the ratio a(n+1)/a(n)·((n+1)/n)^{5/2},
Richardson-extrapolated in 1/n² from n=80 and 99, gives γ ≈ 9.3854 against Drmota–Fusy–Kang–Kraus–Rué's 9.38527 for
unlabeled series-parallel graphs.
Consistency checks satisfied: row sum = A000088(10); T(n,1) = A005195(n) − 1 (forests minus the edgeless graph) for
n = 10..13 (328, 709, 1600, 3657); T(n,n−2) = p(n) − 1 (41, 55); row sums = A000088(10), A000088(11); tw2(12) agrees
between the k=2 and k=3 runs.

## Attacks tried
- **Hidden prior data:** tw ≤ k graphs are disjoint unions of connected ones, so I inverse-Euler-transformed the known
  partial row sums and searched OEIS for the connected tw≤2 / tw≤3 sequences and for the totals. No hits (remy's NOVELTY.md).
- **Pruning soundness:** geng's intermediate graphs are induced subgraphs of the output graph and treewidth is monotone under
  subgraphs, so pruning is exact. Empirically, the pruned partial rows equal the unpruned rows for n ≤ 10, and two
  unrelated pruners give identical output sets at n = 11.
- **AP-rule completeness risk:** if my rule set were incomplete, the AP pruner would wrongly reject partial 3-trees. It agrees
  with the exhaustive elimination pruner on every graph for n ≤ 11 and with dara's code at n = 12.
- **Shared-spec risk in the GF:** both GF implementations come from one derivation, written by dara. I re-derived every
  equation independently and agreed with each. Brute force exercises the whole equation set (all symmetry types occur by
  n = 13), and it matches through n=14. The block series also matches a published table, and the growth constant matches the literature.
  A derivation error that only shows up beyond n=13 would have to leave all of these intact.
- **Not covered:** the elimination pruner was not re-run at n = 12, which would cost about 40 min on 4 cores. At n=12 the
  evidence is AP versus dara's Q-set decider, which are two unrelated deciders.
