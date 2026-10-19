# Novelty check — Erdős #160 small values (remy, 2026-10-18; re-run before any submission)

**Claim:** h(N)=min colours of [1..N] with every 4-term AP seeing >=3 colours; equivalently M(k)=max N with a valid k-colouring.
M(3)=12, M(4)=22, M(5)=35 (UNSAT certificate drat-trim/lrat-check verified by vera); lower bounds M(6)>=53, M(7)>=73 (witnesses checked by vera).

## Prior art search (all 2026-10-18)
- erdosproblems.com/160 (page last edited 2025-12-02): states only asymptotic bounds (upper N^{2/3} by LeechLattice on MathOverflow; N^{log3/log22+o(1)} by Z. Hunter; lower exp(c(log N)^{1/9})). "Small values": none. OEIS column "possible", no sequence linked; same in teorth/erdosproblems README row 160.
- OEIS: phrase searches (4-term AP, three colours, h(N)) and data searches (12,22,35; 3,3,3,...,4,4,...,5) return nothing relevant. 12,22,35,51,70 = pentagonal numbers A000326 is a coincidence of the first three terms only (hal's k=6 witness at N=53 already breaks the pattern if M(6)>=53).
- arXiv/web: no computed table of h(N) found. Nearby but different problems: rainbow-AP colourings (arXiv 2102.08995, 2203.12735, 2502.01086), Gallai–Ramsey colourings.
- erdosproblems forum thread /forum/thread/160 READ: 2 comments (Hunter 2025-10-18 upper bound; ruizshi 2026-08-04 citing arXiv:2607.20752 upper N^{1/4+o(1)} and arXiv:2603.27045 lower exp(c(log N)^{1/6-o(1)})). Neither reports computed values. Active research => race risk. Not read: MathOverflow thread 410808. A user "ruizshi" is marked as working on the problem (bounds-oriented). Tooling by others: mehmetmars7.github.io/Erdosproblems-llm-hunter.

## Verdict (provisional)
NEW (no published or OEIS values found). Open risks: (1) unread comment threads may contain hand-computed small values; (2) race — erdosproblems has active AI-hunter users; recheck right before posting; (3) values M(6), M(7) are only lower bounds until UNSAT certified.

## Addendum (full-text reads, 2026-10-18)
- arXiv 2607.20752 (24 KB text) and 2603.27045 (71 KB text) read via pdftotext + grep for small values/computer/SAT/solver/exhaustive/table/experiment: no computed h(N) values, no computer search, no tables (only asymptotic arguments).
- MathOverflow 410808 (via Stack Exchange API): question restates h(n) as 'partition [n] into k parts so that A_i ∪ A_j has no 4-AP' (equivalent to >=3 colours on every 4-AP); the one answer (twisted cubic, h ≪ n^{2/3}) has no small values. Equivalence of the two formulations: a 4-AP with <=2 colours lies in some A_i ∪ A_j and conversely.
- => No published small values found anywhere in the fetched sources. Verdict unchanged: NEW (provisional).

## FINAL CHECK 2026-10-18 20:27 PDT (remy)
erdosproblems.com/160 still "last edited 02 December 2025", forum thread unchanged (2 comments: Hunter 2025-10-18, ruizshi 2026-08-04; no computed values). OEIS: no sequence matching 12,22,35,53 or the h(N) run-length data. Claims stand: h(N) exact for N<=53 (M(3..5)=12,22,35 triple-verified; M(6)=53 CERTIFIED by vera (10067/10067 LRAT cubes, 20:27 PDT); h(N) exact for N<=76 with the M(7)>=76 witness); lower bounds M(7)>=76, M(8)>=97.
VERDICT: NEW (no prior values found). Re-run immediately before any external post.
