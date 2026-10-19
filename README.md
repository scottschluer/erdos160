# Erdős Problem #160 small values, and graphs counted by treewidth

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23473523.svg)](https://doi.org/10.5281/zenodo.23473523)

Two new results in computational combinatorics, with everything needed to check them.
A team of AI agents produced them on 18 October 2026, and every claim was recomputed by a second agent using independently
written code (see [How this was made](#how-this-was-made)).

A one-page summary is in [`DISCOVERIES.md`](DISCOVERIES.md). Archived on Zenodo:
[10.5281/zenodo.23473523](https://doi.org/10.5281/zenodo.23473523) (all versions; v1.0.0 is
[10.5281/zenodo.23473524](https://doi.org/10.5281/zenodo.23473524)).

## 1. Erdős Problem #160: first exact small values

[Problem #160](https://www.erdosproblems.com/160) asks for h(N), the least number of colours for {1,…,N} such that every
4-term arithmetic progression receives at least 3 distinct colours. Only asymptotic bounds were known. Write M(k) for the
largest N admitting a valid k-colouring.

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| M(k) | 3 | 3 | **12** | **22** | **35** | **53** | ≥ 76 | ≥ 97 |

- Lower bounds are explicit colourings (`results/erdos160-small-values/witnesses/`).
- Upper bounds are SAT refutations with checked DRAT/LRAT proofs. M(6) = 53 was proved by cube-and-conquer over the 10,067
  symmetry classes of colourings of the centre block [23..32], with every cube refuted by an LRAT certificate checked with `lrat-check`.
- Hence h(N) is known exactly for every N ≤ 76. h(77) is 7 or 8.
- Up to colour permutation and reversal, the extremal colourings number 1, 3 and 5 for k = 3, 4, 5 (`extremal/`).

Details: [`results/erdos160-small-values/`](results/erdos160-small-values/) (README, VERIFICATION, NOVELTY).

## 2. Unlabeled graphs counted by treewidth

- [OEIS A362908](https://oeis.org/A362908) (treewidth 2) is extended from n ≤ 9 to **n ≤ 100** by an exact generating
  function. It has two independent implementations and agrees with exhaustive enumeration for every n ≤ 14.
- [A362907](https://oeis.org/A362907) (treewidth 3): new terms a(10..12) = 1292868, 22230001, 404312886.
- [A263294](https://oeis.org/A263294): new rows n = 10 and 11 (all 1,018,997,864 graphs on 11 vertices).
- Two sequences not in OEIS: connected graphs and all graphs with no K4 minor, by number of vertices, n ≤ 100.
- Already published and not claimed: the 2-connected series-parallel counts (Giménez–Noy–Rué, arXiv:0712.1869). They are
  used here as an external check.

Details: [`results/treewidth-counts/`](results/treewidth-counts/).

## Verify it yourself

Requirements: macOS or Linux, `clang`, Python 3.13, network access on first run (to fetch pinned nauty and drat-trim), and `cadical` on PATH.

```sh
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python numpy scipy sympy networkx python-sat numba
verify/build_deps.sh                          # nauty 2.9.3 (sha256-pinned) and drat-trim @2e3b2dc into verify/deps/
results/treewidth-counts/check.sh             # treewidth claims vs claims.json, about 70 s on 4 cores (--full: n = 12, 13)
verify/run_h160_verification.sh               # every colouring, certified UNSAT for M(3..5), DFS counts, about 50 s
JOBS=7 verify/run_h160_verification.sh --m6   # re-certify M(6) = 53, about 3.2 core-hours
```

The exact CNF files for the four upper bounds are in `results/erdos160-small-values/cnf/` with `SHA256SUMS`.

## Layout

| path | contents |
|---|---|
| `results/` | one folder per result: claims, data, README, VERIFICATION (independent check), NOVELTY (literature check) |
| `search/` | code that found the results (SAT encodings, tabu search, geng hooks, the generating function) |
| `verify/` | independent checkers, written from the definitions without reading `search/` |
| `research/` | target surveys and novelty notes |

## How this was made

The work was done by five AI agents (Anthropic's Claude) working as a team in Bullpen, a multi-agent workspace, and
operated by Scott Schluer. The agents were a lead, a search engineer, a counting specialist, an independent verifier and a
researcher. The rule was that no agent verified its own result. Each claim was produced by one agent, recomputed blind
with separate code by another, checked against OEIS and the literature by a third, and re-run cold by a non-author. Each
result folder's README, VERIFICATION and NOVELTY files record who did what. References there such as "room log m42" point
to the team's working chat, which is not included in this repository.

## License

Code: MIT (see `LICENSE`). Data, results and text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
To cite, use `CITATION.cff`.
