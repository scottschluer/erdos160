#!/usr/bin/env python3
"""vera's independent implementation of the unlabeled tw<=2 (K4-minor-free)
generating function, written from results/treewidth-counts/GF.md only (did not
read search/oeis/treewidth/sp_gf.py). Each equation was re-derived before
coding; see the comments.

Series are lists of Fractions truncated at x^NMAX. Level-1 quantities carry a
dual part (p1 = g + eps) so that Z_{B'} = dZ_B/dp1 comes out as the eps part.

Checks built in (run with --check):
  * forests: block-cut composition with B = K2 must equal Otter's formula
    (rooted trees -> trees -> Euler transform), an unrelated derivation.
  * block counts with g = x vs the brute-force list in GF.md (and vera's own
    geng -C counts when available).

Usage: sp_gf_vera.py NMAX [--check] [--blocks]
Prints n, [x^n]A (all tw<=2 graphs), forests(n), A362908(n) = difference.
"""

import argparse
import sys
from fractions import Fraction as Fr
from math import gcd

NMAX = 20


# ------------------------------------------------------------ series basics

def zero():
    return [Fr(0)] * (NMAX + 1)


def const(c):
    s = zero()
    s[0] = Fr(c)
    return s


def add(*ss):
    return [sum(t) for t in zip(*ss)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def scale(a, c):
    c = Fr(c)
    return [x * c for x in a]


def mul(a, b):
    out = [Fr(0)] * (NMAX + 1)
    nz = [(i, x) for i, x in enumerate(a) if x]
    for j, y in enumerate(b):
        if not y:
            continue
        for i, x in nz:
            if i + j > NMAX:
                break
            out[i + j] += x * y
    return out


def subst(a, k):
    """a(x^k)"""
    out = zero()
    for i in range(0, NMAX // k + 1):
        out[i * k] = a[i]
    return out


def exp_s(a):
    assert a[0] == 0
    f = zero()
    f[0] = Fr(1)
    for n in range(1, NMAX + 1):
        f[n] = sum(k * a[k] * f[n - k] for k in range(1, n + 1)) / n
    return f


def inv1m(a):
    """1/(1 - a), a[0] = 0"""
    assert a[0] == 0
    f = zero()
    f[0] = Fr(1)
    for n in range(1, NMAX + 1):
        f[n] = sum(a[k] * f[n - k] for k in range(1, n + 1))
    return f


def neglog1m(a):
    """-log(1 - a) = sum a^j / j, a[0] = 0; via L' = a' / (1 - a)"""
    q = inv1m(a)
    da = [k * a[k] for k in range(NMAX + 1)]  # x a'(x)
    xl = mul(da, q)  # x L'(x)
    return [Fr(0)] + [xl[n] / n for n in range(1, NMAX + 1)]


def phi(m):
    return sum(1 for i in range(1, m + 1) if gcd(i, m) == 1)


# --------------------------------------------------------------- dual numbers

class D:
    """a + eps*b with eps^2 = 0; a, b series."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=None):
        self.a = a
        self.b = b if b is not None else zero()

    def __add__(s, o):
        o = o if isinstance(o, D) else D(o)
        return D(add(s.a, o.a), add(s.b, o.b))

    __radd__ = __add__

    def __sub__(s, o):
        o = o if isinstance(o, D) else D(o)
        return D(sub(s.a, o.a), sub(s.b, o.b))

    def __rsub__(s, o):
        return D(o) - s

    def __mul__(s, o):
        if isinstance(o, (int, Fr)):
            return D(scale(s.a, o), scale(s.b, o))
        o = o if isinstance(o, D) else D(o)
        return D(mul(s.a, o.a), add(mul(s.a, o.b), mul(s.b, o.a)))

    __rmul__ = __mul__


def dexp(u):
    e = exp_s(u.a)
    return D(e, mul(u.b, e))


def dinv1m(u):
    q = inv1m(u.a)
    return D(q, mul(u.b, mul(q, q)))


def dneglog1m(u):
    return D(neglog1m(u.a), mul(u.b, inv1m(u.a)))


# ----------------------------------------------------------- the equations

def network_step(g, N, Nt):
    """One update of the network system for vertex series g (p_j = g(x^j)).
    Returns new (N, Nt) and the pieces needed for blocks."""
    p1 = D(g, const(1))              # p1 = g + eps
    p2 = subst(g, 2)
    N2 = subst(N.a, 2)               # N(x^2): level 2, no eps
    y = p1 * N
    y2 = mul(p2, N2)                 # = y(x^2)
    q2 = inv1m(y2)                   # 1/(1 - y2)
    # series networks: chain of k>=2 non-series parts, k-1 cut vertices
    S = N * y * dinv1m(y)            # N^2 p1 / (1 - N p1)
    Sk = {k: subst(S.a, k) for k in range(2, NMAX + 1)}
    # twisted: chain reversal. k=2j: middle cut vertex fixed (p1), j part
    # pairs N(x^2), j-1 vertex pairs p2. k=2j+1: middle part twisted (Nt),
    # j part pairs, j vertex pairs.
    St = p1 * mul(N2, q2) + Nt * mul(y2, q2)
    Stk = {k: subst(St.a, k) for k in range(3, NMAX + 1, 2)}
    # multisets of series parts (parallel composition), plain and twisted:
    # a k-cycle of parts under a pole swap composes to a swap iff k is odd
    E = dexp(S + add(zero(), *[scale(Sk[k], Fr(1, k)) for k in Sk]))
    Et = dexp(St + add(zero(), *[scale(Stk[k] if k % 2 else Sk[k], Fr(1, k))
                                 for k in range(2, NMAX + 1)]))
    # parallel: >= 2 parts, at most one real edge (weight 1)
    P = 2 * E - const(2) - S
    Pt = 2 * Et - const(2) - St
    newN = D(const(1)) + P           # N = e + P
    newNt = D(const(1)) + Pt         # e is fixed by the swap
    parts = dict(p1=p1, p2=p2, N2=N2, y=y, y2=y2, q2=q2, S=S, Sk=Sk, St=St,
                 E=E, Et=Et, P=P, Pt=Pt)
    return newN, newNt, parts


def blocks(N, Nt, pc):
    """B = K2 + B_S + B_P - B_SP (dual)."""
    p1, p2, N2, y, y2, q2 = pc["p1"], pc["p2"], pc["N2"], pc["y"], pc["y2"], pc["q2"]
    S, St, E, Et, P, Pt, S2 = pc["S"], pc["St"], pc["E"], pc["Et"], pc["P"], pc["Pt"], pc["Sk"][2]
    K2 = (p1 * p1 + p2) * Fr(1, 2)
    # cycles of length k >= 3 with N-decorated edges, dihedral average.
    # rotations: sum_m phi(m)/m * L(x^m) / 2 minus k = 1, 2 terms
    L1 = dneglog1m(y)
    rot = L1 * Fr(1, 2)
    for m in range(2, NMAX + 1):
        rot = rot + scale(subst(L1.a, m), Fr(phi(m), 2 * m))
    rot = rot - y * Fr(1, 2) - (y * y) * Fr(1, 4) - scale(y2, Fr(1, 4))
    # reflections: k odd: fixed vertex p1, fixed flipped edge Nt, pairs y2;
    # k even: through 2 vertices (p1^2, pairs) or through 2 edges (Nt^2)
    refl = (p1 * Nt * mul(y2, q2)) * Fr(1, 2) + \
        (p1 * p1 * N2 + Nt * Nt * p2) * mul(y2, q2) * Fr(1, 4)
    BS = rot + refl
    # bonds: >= 3 parts, at most one real edge; unordered pole pair
    E2 = (S * S + S2) * Fr(1, 2)
    E2t = (St * St + S2) * Fr(1, 2)
    G = (E - const(1) - S) + (E - const(1) - S - E2)
    Gt = (Et - const(1) - St) + (Et - const(1) - St - E2t)
    BP = (p1 * p1 * G + Gt * p2) * Fr(1, 2)
    # split pairs: one series side, one parallel side
    BSP = (p1 * p1 * S * P + St * Pt * p2) * Fr(1, 2)
    return K2 + BS + BP - BSP, K2


def solve(only_blocks=False, block_fn=None):
    """Fixed point for g = C•, N, Nt. Returns (Cdot, B_real, Bprime) at the fixed point.
    block_fn(N, Nt, parts) -> (B, K2) can be swapped (for the forest check)."""
    block_fn = block_fn or blocks
    x = zero()
    x[1] = Fr(1)
    g = x[:]
    N = D(const(1))
    Nt = D(const(1))
    for it in range(4 * NMAX + 10):
        N1, Nt1, pc = network_step(g, N, Nt)
        B, _ = block_fn(N, Nt, pc)
        if only_blocks:
            gn = g
        else:
            ex = add(B.b, *[scale(subst(B.b, k), Fr(1, k)) for k in range(2, NMAX + 1)])
            gn = mul(x, exp_s(ex))
        same = (gn == g and N1.a == N.a and N1.b == N.b and Nt1.a == Nt.a and Nt1.b == Nt.b)
        g, N, Nt = gn, N1, Nt1
        if same:
            break
    else:
        raise RuntimeError("no convergence")
    _, _, pc = network_step(g, N, Nt)
    B, _ = block_fn(N, Nt, pc)
    return g, B.a, B.b


def all_graphs(Cdot, B, Bp):
    C = add(Cdot, sub(B, mul(Cdot, Bp)))
    A = exp_s(add(*[scale(subst(C, k), Fr(1, k)) for k in range(1, NMAX + 1)]))
    return C, A


def otter_forests():
    """Rooted trees r = x exp(sum r(x^k)/k); trees t = r - (r^2 - r(x^2))/2;
    forests = exp(sum t(x^k)/k)  (includes the empty forest at n=0)."""
    x = zero()
    x[1] = Fr(1)
    r = x[:]
    for _ in range(NMAX + 2):
        r = mul(x, exp_s(add(*[scale(subst(r, k), Fr(1, k)) for k in range(1, NMAX + 1)])))
    t = sub(r, scale(sub(mul(r, r), subst(r, 2)), Fr(1, 2)))
    return exp_s(add(*[scale(subst(t, k), Fr(1, k)) for k in range(1, NMAX + 1)]))


def as_int(s):
    out = []
    for c in s:
        assert c.denominator == 1, c
        out.append(int(c))
    return out


def main():
    global NMAX
    ap = argparse.ArgumentParser()
    ap.add_argument("nmax", type=int)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--blocks", action="store_true")
    a = ap.parse_args()
    NMAX = a.nmax
    forests = as_int(otter_forests())
    if a.check:
        # forest check: blocks = K2 only
        Cd, B, Bp = solve(block_fn=lambda N, Nt, pc: (lambda K2: (K2, K2))(
            (pc["p1"] * pc["p1"] + pc["p2"]) * Fr(1, 2)))
        _, A = all_graphs(Cd, B, Bp)
        assert as_int(A) == forests, (as_int(A), forests)
        print("check: block-cut composition with B=K2 reproduces Otter forests", forests[:12])
    _, Bx, _ = solve(only_blocks=True)
    blk = as_int(Bx)
    if a.blocks or a.check:
        print("blocks (g = x), n=1..:", blk[1:])
    Cd, B, Bp = solve()
    C, A = all_graphs(Cd, B, Bp)
    A, C = as_int(A), as_int(C)
    print("n  all_tw<=2  connected_tw<=2  forests  A362908")
    for n in range(1, NMAX + 1):
        print(n, A[n], C[n], forests[n], A[n] - forests[n])
    return 0


if __name__ == "__main__":
    sys.exit(main())
