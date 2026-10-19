# Novelty check — treewidth counts of unlabeled graphs (remy, 2026-10-18; to be re-run before any submission)

**Claim under test (dara, vera diff pending):** new terms for A362908 (tw=2), A362907 (tw=3) and row n=10 (and n>=11 where computed) of A263294.
Candidate values reported in the room: tw=2: a(10)=56756, a(11)=374887; tw=3: a(10)=1292868, a(11)=22230001; row 10 = 1,328,56756,1292868,5502502,4574482,570499,7690,41,1.

## What exists today (fetched live from oeis.org, OEIS last-modified stamp 2026-10-18 21:50 EDT)
- A362908 (tw=2): data 0,0,0,1,4,17,72,323,1639,9203 (n=0..9); links: only Wikipedia "Treewidth"; keywords nonn,more; last history entry 2026-06-28 (Irvine, link fix). **No term beyond n=9, no b-file.**
- A362907 (tw=3): data 0,0,0,0,1,6,53,501,5889,81786 (n=0..9); keywords nonn,hard,more. **No term beyond n=9.**
- A263294 (triangle, tw by n): rows n=1..9 only (last row 1,152,9203,81786,138923,42596,1977,29,1); extended by Rubey May 2023; keyword more. **No row n=10.**
- Searches of OEIS for the connected variants (inverse-Euler of partial sums, vera's numbers 1,1,2,5,15,56,241,1245,7182 and 1,1,2,6,20,102,682,6570,82494) and totals (tw<=2: 1,2,4,10,27,92,360,1715,9356; tw<=3: ...,11,33,145,861,7604,91142): no matching sequences (per vera, m30; I did not independently re-run those).
- FindStat St000272 (treewidth): data only for n<=7, no distribution tables for n>=10 (fetched 2026-10-18).
- Literature: no table of unlabeled graph counts by treewidth found. Related work is labeled/asymptotic: Baste–Noy–Sau arXiv:1604.07273 (labeled, tw<=k), Bodirsky–Giménez–Kang–Noy math/0512435 (series-parallel, labeled+asymptotic unlabeled), Drmota–Fusy–Kang–Kraus–Rué arXiv:1003.4699 (asymptotics). tw<=2 = K4-minor-free; their GF methods could in principle give unlabeled counts, so a published/privately computed list is possible [I], but none found.
- Wider check of "treewidth" near-duplicates in OEIS: A368500 (permutations by incidence-graph treewidth) is unrelated.

## Verdict (provisional)
NEW relative to OEIS/FindStat/literature found as of 2026-10-18, **conditional on** (a) vera's blind diff of dara's numbers matching, (b) an exact-GF cross-check for tw=2 (optional, strong), and (c) re-checking OEIS A362907/A362908/A263294 immediately before submission (people can extend `more` sequences any day; A362907 is flagged `hard`).
Sanity facts supporting correctness (from dara's report, not re-derived by me): row sums = A000088(10)=12005168; T(n,n-2)=p(n)-1; rows 1..9 reproduce OEIS.

## Addendum (full-text reads, 2026-10-18)
- arXiv 1003.4699 (Drmota–Fusy–Kang–Kraus–Rué) and math/0512435 (Bodirsky–Giménez–Kang–Noy) grepped: only asymptotic constants (e.g. gamma≈9.38527 unlabelled series-parallel) and parameter tables; no explicit table of unlabeled series-parallel/K4-minor-free counts by vertex number.
- Unlabeled tw<=2 counts would equal totals of K4-minor-free graphs; not found in any fetched source.

## Status 19:15 — re-check
OEIS A362907/A362908/A263294 unchanged (data still ends at n=9 / row 9). Independently verified by vera (blind): row 10, tw2(10..12) (tw2(12)=2607705), tw3(10..12) (tw3(12)=404312886). Candidate extension: A362908 a(10..12)=56756, 374887, 2607705; A362907 a(10..12)=1292868, 22230001, 404312886.

## Addendum 19:20 — overlap with literature found
- Giménez–Noy–Rué, arXiv:0712.1869, eq.(108): unlabelled **2-connected** series-parallel graphs by vertices: 1,1,2,5,15,51,230,1142,6369,37601,232259,1476120,9599522 (n=2..14). This equals dara's block-level GF output => 2-connected SP counts are NOT new (cite them); they also give an external check of the GF to n=14. Still absent from OEIS.
- Connected / all K4-minor-free and tw<=2 counts: not in 0712.1869 (only 2-connected series + networks eq.109), not in 1003.4699, math/0512435, BFKV pointing paper, arXiv:1511.06037 (full-text grep), not in OEIS (data searches 1,1,2,5,15,56,241,1245 / 1,2,4,10,27,92,360,1715 return nothing).
- Therefore the novel claims are: A362908 extension (n=10..100 if GF validated), A362907 n=10..12, A263294 row 10 (and 11 if finished), and the connected/all K4-minor-free counts (derivable by Euler transform from the same data).

## FINAL CHECK 2026-10-18 20:27 PDT (remy)
Live re-fetch: A362907, A362908, A263294 data unchanged (end n=9 / row 9). OEIS data searches for connected K4-minor-free (1,1,2,5,15,56,241,1245,7182,45477) and all K4-minor-free (1,2,4,10,27,92,360,1715,9356,57085): zero results. Literature overlap limited to the 2-connected series (Giménez–Noy–Rué 0712.1869 eq.108, n<=14; credit them). Verification status per vera: row 10, row 11, tw2 n<=14, tw3 n<=12, GF n<=100 (two implementations).
VERDICT: NEW — A362908 a(10..100), A362907 a(10..12), A263294 rows 10-11, and connected / all K4-minor-free counts. Re-run this check immediately before any submission (OEIS `more` sequences can be extended by anyone at any time).
