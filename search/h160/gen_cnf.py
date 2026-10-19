"""CNF for Erdős #160: k-colour [1..N] so every 4-term AP gets >= 3 distinct colours.

Equivalent: for every pair of colours {c1,c2}, the union of the two colour classes has no 4-AP.

Variables: x(i,c) = "i has colour c" (1<=i<=N, 0<=c<k), y(i,S) = "colour of i is in pair S".
  at-least-one colour per i;  x(i,c) -> y(i,S) for c in S;  for each 4-AP P and pair S: OR_{p in P} -y(p,S).
No at-most-one is needed: dropping colours from a multi-coloured vertex keeps every clause satisfied
(y's are only lower-bounded), so any model yields a proper colouring by taking any one colour per i.
With --amo the at-most-one clauses are added anyway (useful for the decoder / for some solvers).

Symmetry breaking (--sym prec): value precedence — colour c>0 may appear at i only if colour c-1 appears
at some j<i. Encoded with u(i,c) = "colour c appears in 1..i". Precedence constrains the chosen colour,
so it needs AMO: --sym prec implies --amo.

Usage: python gen_cnf.py N k [--sym none|prec] [--amo] > f.cnf     (variable map in header comments)
"""
import argparse, itertools, sys


def build(N, k, sym="prec", amo=False):
    if sym == "prec":
        amo = True
    nv = 0
    def new():
        nonlocal nv
        nv += 1
        return nv
    x = {(i, c): new() for i in range(1, N + 1) for c in range(k)}
    pairs = list(itertools.combinations(range(k), 2))
    y = {(i, S): new() for i in range(1, N + 1) for S in pairs}
    cls = []
    for i in range(1, N + 1):
        cls.append([x[i, c] for c in range(k)])
        if amo:
            for c1, c2 in itertools.combinations(range(k), 2):
                cls.append([-x[i, c1], -x[i, c2]])
        for S in pairs:
            for c in S:
                cls.append([-x[i, c], y[i, S]])
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(1, N - 3 * d + 1):
            P = [a + j * d for j in range(4)]
            for S in pairs:
                cls.append([-y[p, S] for p in P])
    if sym == "prec":
        u = {(i, c): new() for i in range(1, N + 1) for c in range(k)}
        for i in range(1, N + 1):
            for c in range(k):
                # u(i,c) <-> u(i-1,c) or x(i,c)
                prev = u.get((i - 1, c))
                cls.append([-x[i, c], u[i, c]])
                if prev:
                    cls.append([-prev, u[i, c]])
                    cls.append([-u[i, c], prev, x[i, c]])
                else:
                    cls.append([-u[i, c], x[i, c]])
                if c > 0:  # x(i,c) -> u(i-1,c-1)
                    cls.append([-x[i, c]] + ([u[i - 1, c - 1]] if i > 1 else []))
    return nv, cls, x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int); ap.add_argument("k", type=int)
    ap.add_argument("--sym", default="prec", choices=["none", "prec"]); ap.add_argument("--amo", action="store_true")
    a = ap.parse_args()
    nv, cls, x = build(a.N, a.k, a.sym, a.amo)
    out = sys.stdout
    out.write(f"c Erdos160 N={a.N} k={a.k} sym={a.sym} x(i,c)=(i-1)*k+c+1 for 1<=i<=N, 0<=c<k\n")
    out.write(f"p cnf {nv} {len(cls)}\n")
    out.write("".join(" ".join(map(str, c)) + " 0\n" for c in cls))


if __name__ == "__main__":
    main()
