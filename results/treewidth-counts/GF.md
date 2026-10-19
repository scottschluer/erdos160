# Generating-function method for tw ≤ 2 (no K4 minor), unlabeled, counted by vertices

This is the specification for an independent reimplementation. dara's code is
`search/oeis/treewidth/sp_gf.py`; please don't read it if you're reimplementing.

Notation: a cycle-index series Z(p1, p2, ...) is used only through substitutions p_j ← g(x^j), where g is a
power series with g(0) = 0 that plays the role of "one vertex". F(x^k) means "F with every p_j ← g(x^{jk})", which
for an already-evaluated series is just x ↦ x^k. Every equation below is a power-series identity, truncated at x^NMAX.
To get the derivative Z_{F'} = ∂Z_F/∂p1, carry dual numbers: p1 = g(x) + ε, and only level-1 quantities
(the ones not of the form ·(x^k) with k ≥ 2) get an ε part.

## 1. Networks (two poles 0, ∞, not counted as vertices; simple graphs; automorphisms fix each pole)
- e = a single edge between the poles, weight 1.
- N = e + P: non-series networks.
- S = Σ_{k≥2} N^k · p1^{k−1} = N²·p1 / (1 − N·p1). A series network is a chain of k ≥ 2 non-series parts
  joined at k−1 internal cut vertices. Its order is fixed because the poles are fixed.
- E = exp( Σ_{k≥1} S(x^k)/k ), the multiset species E∘S.
- P = e·E_{≥1}(S) + E_{≥2}(S) = (E − 1) + (E − 1 − S) = 2E − 2 − S. A parallel network is a set of ≥ 2 parts,
  at most one of them the real edge e, and the rest series networks.

**Twisted** versions (marked t) sum over automorphisms that **swap** the two poles:
- e_t = 1.
- S_t: reversing a chain of k parts. With y2 = p2 · N(x²):
  - k = 2j: the middle cut vertex is fixed and the parts pair up, giving p1 · p2^{j−1} · N(x²)^j.
  - k = 2j+1: the middle part is twisted, giving N_t · p2^j · N(x²)^j.
  - So S_t = p1·N(x²)/(1 − y2) + N_t·y2/(1 − y2).
- E_t = exp( S_t + Σ_{k≥2} [k odd ? S_t(x^k) : S(x^k)] / k ). In a k-cycle of parts the composite map is a
  pole swap when k is odd and pole-fixing when k is even.
- P_t = 2E_t − 2 − S_t, and N_t = 1 + P_t.

## 2. Blocks: B = K2 + (2-connected SP graphs), via dissymmetry on the SPQR tree
In a 2-connected SP graph the SPQR tree has only S-nodes (cycles) and P-nodes (bonds), and every tree edge
joins an S-node to a P-node. So B₂ = B_S + B_P − B_SP.
- K2 = (p1² + p2)/2.
- B_S: a cycle of length k ≥ 3 on vertices, whose edges are decorated with N (a real edge, or a virtual edge
  whose far side is a P-network), averaged over the dihedral group D_k:
  B_S = Σ_{k≥3} 1/(2k) · [ Σ_{m|k} φ(m)·(p_m·N(x^m))^{k/m} + refl_k ], where
  - k odd: refl_k = k · p1 · N_t · y2^{(k−1)/2}
  - k even: refl_k = (k/2)·p1²·p2^{(k−2)/2}·N(x²)^{k/2} + (k/2)·p2^{k/2}·N_t²·N(x²)^{(k−2)/2}
  - (closed form: with y = p1·N and L = −log(1 − y),
    B_S = ½Σ_{m≥1} (φ(m)/m)·L(x^m) − y/2 − y²/4 − y2/4 + ½·p1·N_t·y2/(1−y2) + ¼·(p1²·N(x²) + p2·N_t²)·y2/(1−y2))
- B_P: a bond {u, v} with a set of ≥ 3 parts, at most one of them a real edge and the rest series networks.
  Swapping u and v twists every part.
  - G = E_{≥2}(S) + E_{≥3}(S) = (E − 1 − S) + (E − 1 − S − (S² + S(x²))/2)
  - G_t = (E_t − 1 − S_t) + (E_t − 1 − S_t − (S_t² + S(x²))/2)
  - B_P = ½·(p1²·G + p2·G_t)
- B_SP: a split pair {u, v} with one series network and one parallel network:
  B_SP = ½·(p1²·S·P + p2·S_t·P_t).

## 3. Connected and all graphs (block-cut tree dissymmetry)
- Rooted connected: C•(x) = x · exp( Σ_{k≥1} B'_{C•}(x^k) / k ), where B'_{C•} = Z_{B'} with g = C•.
- Connected: C = C• + B_{C•} − C• · B'_{C•}.
- All: A = exp( Σ_{k≥1} C(x^k)/k ). Then A362908(n) = [x^n]A − A005195(n), since tw ≤ 1 graphs are forests.
- Solve by fixed-point iteration. Each pass fixes at least one more coefficient. Start from g = x and networks at 0 (N = N_t = 1).

## Checks
- With g = x, [x^n]B counts blocks: 0, 1, 1, 2, 5, 15, 51, 230, 1142, 6369, 37601, 232259 (n = 1..12).
- Connected and all-graph counts must match brute force: connected tw ≤ 2 for n=1..10 is
  1,1,2,5,15,56,241,1245,7182,45477; all tw ≤ 2 is ...,57085 (10), 375597 (11), 2609306 (12).
- Growth constant: unlabeled SP graphs grow like c·n^{−5/2}·γ^n with γ ≈ 9.38527 (Drmota–Fusy–Kang–Kraus–Rué 2011).
