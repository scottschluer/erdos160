# What we found (2026-10-18)

Two new results in computational combinatorics. Every claim was produced by one teammate, recomputed with
independently written code by another (vera), and checked against OEIS and the literature by a third (remy).
Nothing has been published externally yet. Draft submission texts are in each result folder.

## 1. Erdős Problem #160: first exact small values — `results/erdos160-small-values/`

h(N) is the least number of colours for {1..N} such that every 4-term arithmetic progression sees at least 3 colours.
erdosproblems.com lists only asymptotic bounds and "small values: none". Write M(k) for the largest N with a valid
k-colouring.

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| M(k) | 3 | 3 | **12** | **22** | **35** | **53** | ≥ 76 | ≥ 97 |

- This gives h(N) exactly for every N ≤ 76: 3 on [4,12], 4 on [13,22], 5 on [23,35], 6 on [36,53], 7 on [54,76].
- Upper bounds are SAT refutations with checked DRAT/LRAT certificates. M(5)=35 was confirmed three ways: hal's
  kissat run, vera's cadical + drat-trim + lrat-check run on her own encoding, and vera's plain backtracking DFS.
- M(6)=53: N=54 is UNSAT by cube-and-conquer over the 10067 orbit representatives of colourings of the centre
  block [23..32]. vera certified every cube on her own CNF with cadical --lrat and checked each with lrat-check:
  10067/10067 verified, 3.2 core-hours. hal's uncertified run on his own pipeline agrees.
  vera independently generated the same cube set and checked that it covers every valid colouring up to colour
  permutation and reversal.
- The extremal colourings are nearly unique. Up to colour permutation and reversal there is exactly 1 for k=3,
  3 for k=4 and 5 for k=5, counted by SAT enumeration and independently by DFS. All are listed in `extremal/`.
- 12, 22, 35 are pentagonal numbers, but M(6) = 53 ≠ 51 shows that this is a coincidence.

## 2. Unlabeled graphs counted by treewidth — `results/treewidth-counts/`

OEIS A362908 (tw = 2), A362907 (tw = 3) and the triangle A263294 stopped at n = 9.

- **A362908 extended from 10 terms to 101 (n ≤ 100)** using an exact generating function for K4-minor-free graphs.
  The GF combines networks with twisted cycle indices, SPQR dissymmetry for blocks, the block-cut tree, and an
  Euler transform. It has two independent implementations that agree on all 600 values. It also matches exhaustive
  generation for every n ≤ 14 (n = 14 was predicted by the GF before the brute force finished) and the published 2-connected counts (Giménez–Noy–Rué) up to n = 14. Its fitted growth
  constant, 9.38526, agrees with Drmota et al.'s 9.38527 to within about 1e-5.
- **A362907: a(10..12) = 1292868, 22230001, 404312886.** These are brute force, with two independent pipelines
  that agree blind.
- **A263294 rows 10 and 11.** Row 11 (all 1,018,997,864 graphs on 11 vertices) is 1, 709, 374887, 22230001,
  236650986, 532355501, 217202772, 10149899, 33052, 55, 1. Both rows matched blind between two pipelines.
- **Two sequences not in OEIS**, counted by vertices: connected K4-minor-free graphs (1, 1, 2, 5, 15, 56, 241,
  1245, 7182, 45477, …) and all K4-minor-free graphs (1, 2, 4, 10, 27, 92, 360, 1715, 9356, 57085, …).
- Re-check: `results/treewidth-counts/check.sh` (about 3 min).

## Reproduce
- `results/treewidth-counts/check.sh`: rebuilds everything, runs brute force for n ≤ 11 and the GF to n = 100, and
  compares against `claims.json` (ALL OK, about 70 s wall on 4 cores; add `--full` for n = 12, 13).
- `verify/run_h160_verification.sh`: checks all witnesses, re-derives and certifies the UNSATs for M(3..5)
  (cadical + drat-trim + lrat-check) and runs the exhaustive DFS counts (about 50 s). `--m6` re-certifies
  M(6) (about 4 core-hours).
- tess ran both cold as a non-author on 2026-10-18, and both passed.

## What didn't pan out (and why)

- **Record tables** (covering designs, covering arrays, constant-weight codes): automated and LLM-driven searches
  already swept them in 2026 (Rosin, Echols and others). hal ran a sweep of 148 stale LJCR entries and beat none.
  The covering-array tables are now behind a login, so novelty could not be checked.
- **Written-on-the-Wall II conjectures #19, 40, 61, 133, 198a**: no counterexample among the 11.7M connected graphs
  with n ≤ 10. The lane was parked because other groups swept these conjectures this month and
  #100 was proved in Aug 2026.
- **Green's problem #27**: published in OEIS (A398173) in Jul 2026 before we got to it.

## Team
tess (lead; WoWII; #160 extremal structure and M(8)), hal (#160 search and SAT), dara (treewidth counts and GF),
vera (independent verification of everything), remy (literature and novelty).
