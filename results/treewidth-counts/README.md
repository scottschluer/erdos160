# New terms: unlabeled graphs counted by treewidth (OEIS A362908, A362907, A263294)

Author of the search code: dara. Independent verification: vera (`verify/`, own code, own geng build).
Novelty: remy, see `NOVELTY.md`.

## Claim

Number of graphs on n unlabeled nodes with treewidth exactly k:

| n | tw=2 (A362908) | tw=3 (A362907) |
|---|---|---|
| 9 (known) | 9203 | 81786 |
| **10** | **56756** | **1292868** |
| **11** | **374887** | **22230001** |
| **12** | **2607705** | **404312886** |
| **13** | **18828907** | |
| **14** | **139869316** | |
| 15..100 | `gf/b362908.txt` (GF) | |

**A362908 through n=100** (`gf/b362908.txt`, b-file format) comes from an exact generating function (`GF.md`,
`search/oeis/treewidth/sp_gf.py`). It agrees with exhaustive generation for every n ≤ 14.
The same computation also gives these, by number of vertices (`gf/`):
- unlabeled blocks (K2 + 2-connected series-parallel graphs): 0, 1, 1, 2, 5, 15, 51, 230, 1142, 6369, 37601, 232259, ...
  This is **not new**: Giménez, Noy and Rué list it through n=14 (arXiv:0712.1869, eq. (108)). Ours matches
  all their terms, which makes it an external check of the block level of the GF. It is still absent from OEIS.
  The following two are not in OEIS and were not found in the literature (see NOVELTY.md):
- connected graphs with no K4 minor: 1, 1, 2, 5, 15, 56, 241, 1245, 7182, 45477, 306261, 2159822, ...
- all graphs with no K4 minor (tw ≤ 2): 1, 2, 4, 10, 27, 92, 360, 1715, 9356, 57085, 375597, 2609306, ...

New row of the triangle A263294, T(n,k) for tw k = 0..n-1:

- **n=10: 1, 328, 56756, 1292868, 5502502, 4574482, 570499, 7690, 41, 1** (sum 12005168 = A000088(10))
- **n=11: 1, 709, 374887, 22230001, 236650986, 532355501, 217202772, 10149899, 33052, 55, 1** (sum 1018997864 =
  A000088(11); unpruned run over all graphs, 1262 CPU-s; vera's independent run matches it blind)

Prior state (OEIS, checked 2026-10-18): A362908 and A362907 had n=0..9 and A263294 had rows n=1..9, all
marked `more`, with no b-files. They were computed by brute force in Sage (`g.treewidth()` over `graphs(n)`).

## Method

`search/oeis/treewidth/`:

- `geng_tw.c` adds PRUNE/OUTPROC/SUMMARY hooks to nauty 2.9.3 `geng`. geng builds each graph by adding
  vertices 0, 1, 2, ..., and every intermediate graph is an induced subgraph of the final one. tw ≤ k is closed under
  taking subgraphs, so pruning every intermediate graph with tw > k is exact. The search then grows with the
  number of answers instead of the number of all graphs.
- `tw.h` holds the deciders:
  - **A** `tw_le`: the exact Q-set criterion of Bodlaender, Fomin, Koster, Kratsch and Thilikos (2006). tw(G) ≤ k
    iff there is a vertex order where each v_i has at most k vertices outside {v_1..v_i} reachable from v_i
    through {v_1..v_{i-1}}. It runs as a DFS over eliminated sets, memoised per subset. It never builds a fill graph.
  - **R** `tw_le_reduce`: safe reductions, then A on whatever is left. The reductions are: delete vertices of
    degree ≤ 1, and eliminate vertices of degree ≤ k that are simplicial or almost simplicial. Each step keeps
    "tw ≤ k" equivalent because G/vw is a minor of G and tw(G) ≤ max(deg v, tw(G')).
  - **C** `sp_reducible`: series-parallel reduction, which decides tw ≤ 2 (no K4 minor).
  - `tw_exact`: lower bound from degeneracy, upper bound from min-fill, then A for each k in between.
- `geng_twpp` is the same build with the hook also used as geng's PREPRUNE, i.e. before the canonicity test.
  It produces the same output set and runs faster.
- `sp_gf.py`: the enumeration-free third method for tw ≤ 2, specified in `GF.md`. It uses networks with
  pole-fixing and pole-swapping (twisted) cycle indices, dissymmetry on the SPQR tree for blocks
  (B = K2 + B_S + B_P − B_SP), the block-cut-tree formula C = C• + B(C•) − C•·B'(C•), and an Euler transform.
  It is exact rational arithmetic and takes 45 s for n ≤ 100.
- `run.sh` splits a run into res/mod parts in parallel. `merge.py` sums the per-(tw, edges) cells into `summary.json`.

## Verification

1. Rows n=1..9 of A263294 and both columns n≤9 are reproduced exactly, by the unpruned run and by both pruned runs.
2. Row n=10 sums to A000088(10) = 12005168. T(10,1) = 328 = A005195(10) − 1 (forests minus the edgeless
   graph). The dense end gives T(n,n−2) = p(n) − 1, i.e. 41 at n=10 (and 55 at n=11). Proof that
   tw(G) ≥ n−2 iff the complement Ḡ is a star forest:
   - (⇐) Look at the first vertex eliminated. If it is a leaf of a star in Ḡ, it has degree n−2 in G. If it is
     isolated in Ḡ, it has degree n−1. If it is the centre of a star, filling its neighbourhood adds every other
     Ḡ-edge back into G, which leaves K_{n−1}.
   - (⇒) If Ḡ contains a triangle abc, eliminate a, b, c first. If Ḡ contains a path a-b-c-d, eliminate b and then
     c. Either way each eliminated vertex has at most n−3 neighbours, so tw ≤ n−3.
   Star forests on n vertices correspond to partitions of n, and we exclude the edgeless one.
3. Pruned and unpruned generation agree at n=10 (tw 2: 56756, tw 3: 1292868) and n=11 (374887, 22230001).
4. Deciders A and R agree on every output graph at n=10 (TWCHECK=1 compares R's classification with tw_exact)
   and on the n=11 tw≤3 counts (separate pruned runs). At n=12, pruning with pure A (`raw/n12_K3_A`, 5776 CPU-s)
   gives per-(tw, edges) cells identical to the R run: tw3 = 404312886. C agrees with A/R on every output graph
   wherever `TWCHECK=1` was set. The `mismatches` counter is 0 in every `summary.json`.
5. Euler transform: tw ≤ k is closed under disjoint unions and components, so the totals must equal the Euler
   transform of the connected counts (`geng -c` runs, a different generation tree). This is checked by
   `euler_check.py`. OK for every n ≤ 12, for both tw ≤ 2 and tw ≤ 3 (`raw/conn/`). The connected tw ≤ 2 counts
   from geng -c also equal the GF's connected series for every n ≤ 12.
6. **Independent blind check by vera.** She used her own geng build and her own deciders (fill-graph elimination
   game, series-parallel reduction, Arnborg–Proskurowski rules). Her numbers match row n=10, tw2(11) and
   tw3(11) exactly. She then matched tw2(12) and **tw3(12) = 404312886** blind (`VERIFICATION.md`). She also
   reimplemented the tw ≤ 2 GF from `GF.md` alone (`verify/treewidth/sp_gf_vera.py`), and it agrees on all six
   series for n = 1..100.

7. **Generating function vs. exhaustive generation (tw = 2).** `sp_gf.py` shares no code or algorithm with the
   generator. It reproduces A362908 for n ≤ 9 and the new brute-force values for n = 10..13, plus the
   connected counts for n ≤ 10 (geng -c). For n=13, the brute-force output was already on disk when the GF
   first ran, but nobody had read it. **n=14 was a true out-of-sample test**: the GF predicted 139869316 (posted at
   19:16), and exhaustive generation finished at 20:18 with 139869316 (`raw/n14_K2_R`, 9090 CPU-s, 73e9 prune calls).
8. **Published block counts.** Our 2-connected SP counts for n=2..14 (..., 232259, 1476120, 9599522) equal
   Giménez–Noy–Rué, arXiv:0712.1869, eq. (108).
9. **Asymptotics.** Fit a(n) ~ c·n^{−5/2}·γ^n to the corrected ratios over n ≤ 100 (`growth_fit.py`,
   `gf/growth_fit.txt`). This gives γ ≈ 9.38526 for both connected and all K4-minor-free graphs, which matches
   the growth constant 9.38527 for unlabeled series-parallel graphs (Drmota, Fusy, Kang, Kraus, Rué,
   *Asymptotic study of subcritical graph classes*, SIAM J. Discrete Math. 2011) to within about 1e-5. The fits of
   order 2-4 give 9.38497-9.38528.

## Proposed OEIS updates
- A362908: b-file n = 0..100 (`gf/b362908.txt`).
- A362907: a(10..12) = 1292868, 22230001, 404312886.
- A263294: rows n=10 and 11.
- New sequence: connected graphs on n unlabeled nodes with no K4 minor (treewidth ≤ 2), n ≥ 1:
  1, 1, 2, 5, 15, 56, 241, 1245, 7182, 45477, 306261, 2159822, 15743944, 117755753, ... (`gf/connected_tw_le2.txt`)
- New sequence: graphs on n unlabeled nodes with no K4 minor (treewidth ≤ 2), n ≥ 1:
  1, 2, 4, 10, 27, 92, 360, 1715, 9356, 57085, 375597, 2609306, 18832565, 139877915, ... (`gf/all_tw_le2.txt`)
- Possible new sequence, citing Giménez–Noy–Rué for n ≤ 14: 2-connected series-parallel graphs on n unlabeled
  nodes (`gf/blocks.txt` minus the K2 term).

## Reproduce

One command re-checks every claim in `claims.json`: `results/treewidth-counts/check.sh` (quick, 73 s wall on 4 cores; prints ALL OK),
or `check.sh --full` (adds n=12 tw≤3 and n=13 tw≤2, ~45 CPU-min). The individual steps are:

```sh
search/oeis/treewidth/build.sh                      # nauty 2.9.3 source (sha256-checked) + hooks -> search/bin/
R=search/oeis/treewidth/run.sh; O=results/treewidth-counts/raw
$R 10 4 $O/n10_all_A TWCHECK=1                      # full row n=10, ~12 s CPU
$R 12 4 $O/n12_K3_R TWK=3                           # tw<=3 at n=12, ~2300 s CPU
GENGBIN=geng_twpp $R 14 4 $O/n14_K2_R TWK=2         # tw<=2 at n=14
.venv/bin/python -I search/oeis/treewidth/euler_check.py "$O/conn/n*_K3_R" "$O/n*_K3_R" 3
.venv/bin/python -I search/oeis/treewidth/sp_gf.py 100 > gf.txt   # GF, ~45 s; columns: n blocks connected all forests tw==2
.venv/bin/python -I search/oeis/treewidth/growth_fit.py gf.txt
```

Timings (Apple M-series, 4 processes, CPU seconds summed): n=11 tw≤3 62 s; n=12 tw≤2 63 s; n=12 tw≤3 2292 s
(11 min wall, 406,922,192 graphs output); n=13 tw≤2 1053 s; n=14 tw≤2 9090 s (geng_twpp); full n=11 row 1262 s.
