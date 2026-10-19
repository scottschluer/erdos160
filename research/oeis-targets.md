# Lane B: OEIS extension targets (dara, 2026-10-18)

Method: full OEIS `stripped.gz` + `names.gz` dumps (Oct 18 2026) filtered offline for short, crisply defined
counting sequences (`search/oeis/offline_filter.py`), then JSON for each shortlisted A-number to check
keywords, offset, b-file, and edit history.

## Pick: treewidth counts of unlabeled graphs

| A-number | definition | known | last data edit |
|---|---|---|---|
| A362908 | # graphs on n unlabeled nodes with treewidth 2 | n=0..9 (`more`) | created May 2023 (Rubey); Jun 2026 edit = link fix only |
| A362907 | # graphs on n unlabeled nodes with treewidth 3 | n=0..9 (`hard,more`) | same |
| A263294 | triangle T(n,k) = # graphs on n nodes with treewidth k | rows n=1..9 (`tabl,more`) | Rubey May 2023 |

No b-files. The original computation was Sage `g.treewidth()` over `graphs(n)`, i.e. brute force over all graphs.

Why this is a good target:
- **Hereditary (minor-closed) property**: tw ≤ k is closed under taking induced subgraphs, so geng can prune any
  intermediate graph with tw > k. The search then grows with the number of *answers* (~12-14x per n for tw 3,
  ~5.6x per n for tw 2) instead of the number of all graphs (~160x per n at n=11).
- Projected reach: tw 2 to n≈15, tw 3 to n≈12, plus full A263294 rows n=10 (12M graphs, exact tw DP) and maybe n=11.
- Crisp definition, exact answers, and built-in consistency checks: each row must sum to A000088(n); columns
  0 and 1 must match edgeless (1) and forests minus edgeless (A005195(n)-1); everything for n≤9 must match OEIS.
- Two genuinely different deciders exist: (i) exact elimination-ordering DP over vertex subsets (any k);
  (ii) for k=2, series-parallel reduction (no K4 minor ⇔ reducible by deleting deg≤1 and suppressing deg-2 vertices).
  The unpruned pipeline (all graphs, degeneracy filter, DP) is an independent cross-check of the pruned one.

## Alternates (all `more`, no b-file, n=1..10 known, so a(11) needs all 1.02e9 graphs on 11 nodes; ~1 term each)

| A-number | definition | note |
|---|---|---|
| A332625 | # graphs with domination number 2 | cheap bitmask check; full domination distribution must sum to A000088(11) |
| A332406 | # graphs with total domination number 2 | same pass as above |
| A340486 | # graphs with independence number = clique number | cheap with bitmask clique search |
| A264683 | # graphs satisfying Ore's condition | trivial check; dense, could prune via complement |
| A135445 | # connected graphs: two vertices with ≥2 common neighbours must be adjacent | extended Jan 2026 by Zabolotskii (active), skip |

Rejected: A126728-A126735 (edge chromatic number; expensive per graph, ~1 term); A242952 (eigenvalue
distinctness, numerically delicate); A243048 (Tutte uniqueness, very hard); famous `hard` sequences (Dedekind,
polycubes, Golomb), which have active record-chasers.
