# Draft OEIS edits for the treewidth results (not yet submitted)

Before submitting, re-check that A362907, A362908 and A263294 have not been extended since 2026-10-18,
and that no sequence with the data below has appeared (search the first ~10 terms).

## A362908 (Number of graphs on n unlabeled nodes with treewidth 2)
- Data: extend through a(20) or so, and attach `gf/b362908.txt` as the b-file (n = 0..100).
- Comment: "a(n) = A?????? (graphs with no K4 minor) - A005195(n) for n >= 1, since the graphs of treewidth at
  most 2 are exactly the K4-minor-free graphs and those of treewidth at most 1 are the forests."
- Comment: "a(10)-a(13) were confirmed by exhaustive generation (nauty geng with treewidth pruning, two independent
  implementations). The b-file was computed from the cycle-index decomposition of series-parallel graphs (networks,
  SPQR-tree dissymmetry, block decomposition), again with two independent implementations."
- Links: b-file; data and code at https://github.com/scottschluer/erdos160 (archived at
  https://doi.org/10.5281/zenodo.23473523); Giménez, Noy and Rué, arXiv:0712.1869 (2-connected SP counts); Drmota, Fusy, Kang, Kraus and Rué,
  Asymptotic study of subcritical graph classes, SIAM J. Discrete Math. 25 (2011) (growth constant 9.38527...).
- Extensions line: "a(10)-a(100) from <name>, Oct 2026".

## A362907 (Number of graphs on n unlabeled nodes with treewidth 3)
- Append: a(10) = 1292868, a(11) = 22230001, a(12) = 404312886.
- Comment: "a(10)-a(12) computed by exhaustive generation with pruning on tw <= 3, which is closed under
  subgraphs, and confirmed by an independent implementation."

## A263294 (Triangle T(n,k): number of unlabeled graphs with n vertices and treewidth k)
- Append row 10: 1, 328, 56756, 1292868, 5502502, 4574482, 570499, 7690, 41, 1.
- Append row 11: 1, 709, 374887, 22230001, 236650986, 532355501, 217202772, 10149899, 33052, 55, 1.
- Comment: "T(n,n-2) = A000041(n) - 1 for n >= 2: tw(G) >= n-2 iff the complement of G is a star forest."
  The proof is in README.md.

## New: Number of connected graphs on n unlabeled nodes with no K4 minor (treewidth <= 2)
- Offset 1. Data (`gf/connected_tw_le2.txt`): 1, 1, 2, 5, 15, 56, 241, 1245, 7182, 45477, 306261, 2159822,
  15743944, 117755753, 898802576, 6975678179, 54900229556, 437268737047, 3518996258094, 28578089737273, ...
- Formula: the inverse Euler transform of the next sequence. Asymptotically c n^(-5/2) gamma^n with
  gamma = 9.38527... (DFKKR 2011).
- Xrefs: A362908, A263294, A005195, A000055.

## New: Number of graphs on n unlabeled nodes with no K4 minor (treewidth <= 2)
- Offset 1 (or 0 with a(0)=1). Data (`gf/all_tw_le2.txt`): 1, 2, 4, 10, 27, 92, 360, 1715, 9356, 57085, 375597,
  2609306, 18832565, 139877915, 1062192529, 8211176932, 64419524696, 511751454418, 4109380741536, ...
- Formula: the Euler transform of the previous sequence; a(n) = A362908(n) + A005195(n).

## Possibly new: Number of 2-connected series-parallel graphs on n unlabeled nodes
- Offset 3: 1, 2, 5, 15, 51, 230, 1142, 6369, 37601, 232259, 1476120, 9599522, 63536701, ... (`gf/blocks.txt`
  without the n=2 term, which is K2). This is published through n=14 in Giménez–Noy–Rué (arXiv:0712.1869,
  eq. (108)), so credit them; it is not in OEIS.
