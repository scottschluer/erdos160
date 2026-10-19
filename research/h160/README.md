# Erdős Problem #160 — small values of h(N)

Source: https://www.erdosproblems.com/160 (fetched 2026-10-18; page last edited 2025-12-02). Statement (verbatim from page):

> Let h(N) be the smallest k such that {1,…,N} can be coloured with k colours so that every four-term arithmetic progression
> contains at least three distinct colours. Estimate h(N).

Known (page): upper h(N) ≪ N^{2/3} (LeechLattice, MathOverflow); h(N) ≪ N^{log3/log22+o(1)} ≈ N^0.355 (Zach Hunter);
lower h(N) ≫ exp(c (log N)^{1/9}) (Hunter's observation + Bloom–Sisask). Status open. "Small values: none listed."
OEIS: marked "Possible", no sequence linked. Formal statement: google-deepmind/formal-conjectures ErdosProblems/160.lean.
Source refs on page: Erdős–Freud, [Er89].

Precise definition used: 4-AP = {a, a+d, a+2d, a+3d} ⊂ [1,N], d ≥ 1. Colouring c:[N]→[k] valid iff every 4-AP has |c(AP)| ≥ 3.
Equivalent dual sequence: M(k) = max N admitting a valid k-colouring (h(N) ≤ k ⇔ N ≤ M(k)); h is non-decreasing in N (restriction).

## Probe results (remy, h.py = pysat/CaDiCaL, at-most-one colour/vertex, first-use symmetry breaking)
h(N)=3 for 4≤N≤12; 4 for 13≤N≤22; 5 for 23≤N≤35; 6 for 36≤N≤≥49 (k=5 UNSAT at N=36 took 46 s)  => M(3)=12, M(4)=22, M(5)=35, M(6)≥49 (N=50 slow at k=6).
Note 12,22,35 are pentagonal (A000326) — likely coincidence; M(6)=51 would continue it.
These are unverified-by-independent-checker; UNSAT claims need DRAT/LRAT proofs. Note: N≤3 trivially 1 colour (no 4-AP).

## Novelty pre-check (remy, 2026-10-18) — not final
- erdosproblems.com/160: no small values; OEIS column = "possible" (teorth/erdosproblems README row 189: none linked).
- OEIS search for 12,22,35 / h(N) description: only unrelated hits (pentagonal numbers etc.).
- Literature search: no table of h(N) small values found; the Hunter/LeechLattice bounds live in MathOverflow + erdosproblems comments (not read directly).
  Related but different: rainbow-AP / Gallai-Ramsey colourings (arXiv 2102.08995, 2203.12735, 2502.01086).
- Risk: erdosproblems has active AI-hunter tooling (mehmetmars7.github.io/Erdosproblems-llm-hunter) and a user (ruizshi) marked 'working on it'. Re-check right before publishing.
