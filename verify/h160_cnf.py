#!/usr/bin/env python3
"""Independent CNF encoder for Erdős #160: "there is a k-colouring of
{1..N} in which every 4-AP gets >= 3 distinct colours".

Encoding (direct, no auxiliary variables):
  x(i, c) = (i - 1) * k + c   for i in 1..N, c in 1..k   ("i has colour c")
  ALO  : x(i,1) v ... v x(i,k)                        for every i
  AMO  : -x(i,c) v -x(i,c')                           for every i, c < c'
         (mandatory: AP clauses use positive literals of the *other*
         colours, so without AMO "every x true" satisfies everything)
  AP   : for every 4-AP P and every colour pair {c1, c2} (c1 < c2; for k = 2
         the single pair), the clause  OR_{p in P} OR_{c not in {c1,c2}} x(p,c)
         says "P is not coloured inside {c1, c2}". For k <= 2 every AP is
         inside a pair, so the clause is empty (formula trivially UNSAT
         whenever a 4-AP exists).
  SB   : (--sb) value precedence: colour c >= 2 may be used at i only if
         colour c-1 is used at some i' < i:
             -x(i,c) v x(1,c-1) v ... v x(i-1,c-1)
         Sound: relabel the colours of any valid colouring by order of first
         appearance; validity only depends on the partition into classes.

Soundness for UNSAT: every valid colouring's one-hot encoding satisfies
ALO + AMO + AP, and after relabelling also SB. So UNSAT of this CNF proves
no valid k-colouring of {1..N} exists, i.e. h(N) > k, M(k) < N.

Usage: h160_cnf.py N K OUT.cnf [--sb]
"""

import argparse
from itertools import combinations


def clauses(N, k, sb=False):
    x = lambda i, c: (i - 1) * k + c  # noqa: E731
    cl = [[x(i, c) for c in range(1, k + 1)] for i in range(1, N + 1)]
    for i in range(1, N + 1):
        for c1, c2 in combinations(range(1, k + 1), 2):
            cl.append([-x(i, c1), -x(i, c2)])
    pairs = list(combinations(range(1, k + 1), 2)) or [(1, 1)]
    for d in range(1, N):
        for a in range(1, N - 3 * d + 1):
            P = [a + j * d for j in range(4)]
            for c1, c2 in pairs:
                cl.append([x(p, c) for p in P for c in range(1, k + 1)
                           if c not in (c1, c2)])
    if sb:
        for c in range(2, k + 1):
            for i in range(1, N + 1):
                cl.append([-x(i, c)] + [x(j, c - 1) for j in range(1, i)])
    return N * k, cl


def write_dimacs(path, nvars, cl, comment=""):
    with open(path, "w") as f:
        if comment:
            f.write(f"c {comment}\n")
        f.write(f"p cnf {nvars} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")


def decode(model, N, k):
    """Colour of each i from a model (list of ints); exactly one must be true."""
    true = {v for v in model if v > 0}
    out = []
    for i in range(1, N + 1):
        cs = [c for c in range(1, k + 1) if (i - 1) * k + c in true]
        if len(cs) != 1:
            raise ValueError(f"model gives {i} colours {cs}")
        out.append(cs[0])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("N", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("out")
    ap.add_argument("--sb", action="store_true")
    a = ap.parse_args()
    nv, cl = clauses(a.N, a.k, a.sb)
    write_dimacs(a.out, nv, cl, f"erdos160 N={a.N} k={a.k} sb={a.sb} (vera)")
    print(f"wrote {a.out}: {nv} vars, {len(cl)} clauses")


if __name__ == "__main__":
    main()
