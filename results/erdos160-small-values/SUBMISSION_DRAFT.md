# Draft submission texts: Erdős #160 small values (not yet posted)

Status: all exact values below (M(1..6)) are certified; see VERIFICATION.md. Lower bounds for M(7), M(8) are explicit colourings.

---

## 1. OEIS: new sequence M(k)

**Name:** Largest N such that {1,...,N} can be colored with n colors so that every 4-term arithmetic progression
receives at least 3 distinct colors.

**Data:** 3, 3, 12, 22, 35, 53

**Offset:** 1

**Comments:**
- Dual of Erdős Problem #160: if h(N) is the least number of colors such that every 4-term AP in {1..N} gets
  at least 3 colors, then h(N) = min{ n : N <= a(n) }.
- Equivalently, a(n) is the largest N such that {1..N} can be partitioned into n classes with the union of any two
  classes free of 4-term APs.
- a(1) = a(2) = 3, since {1,2,3,4} needs 3 colors.
- Up to permuting colors and reversing, the extremal colorings are unique for n=3 (0 0 1 2 1 0 2 1 0 1 2 2).
  There are 3 for n=4 and 5 for n=5.
- a(7) >= 76 and a(8) >= 97 (explicit colorings found by tabu search).
- Lower bounds come from explicit colorings. Upper bounds are SAT proofs: DRAT/LRAT certificates checked with
  drat-trim and lrat-check for n <= 5. For n = 6 the proof is a cube-and-conquer over the 10067 orbit
  representatives of the colorings of the central block [23..32], each cube refuted with an LRAT certificate.

**Links:** Erdős Problems, Problem 160 (https://www.erdosproblems.com/160).

**Cross-refs:** A003003 (largest 4-AP-free subset of [n]), A000326 (pentagonal numbers: agrees for n=3..5 only).

**Keywords:** nonn, hard, more

---

## 2. Comment for the erdosproblems.com/160 forum thread

> Small values. Write M(k) for the largest N such that [N] has a valid k-colouring (so h(N) = min{k : N ≤ M(k)}).
> SAT computations with independently checked certificates give M(3)=12, M(4)=22, M(5)=35 and M(6)=53.
> Hence h(N)=3 for 4≤N≤12, h(N)=4 for 13≤N≤22, h(N)=5 for 23≤N≤35, h(N)=6 for 36≤N≤53 and h(N)=7 for 54≤N≤76.
> Explicit colourings also give M(7) ≥ 76 and M(8) ≥ 97.
> Extremal colourings are rare: up to colour permutation and reversal there is exactly one for k=3
> (0 0 1 2 1 0 2 1 0 1 2 2), three for k=4 and five for k=5.
> The first terms 12, 22, 35 are pentagonal numbers, but M(6) = 53 ≠ 51 breaks the pattern.
> Witnesses, CNFs, the cube set and the checkers: https://github.com/scottschluer/erdos160
> (archived at https://doi.org/10.5281/zenodo.23473523).
