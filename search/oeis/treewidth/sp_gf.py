"""Exact counts of unlabeled graphs with treewidth <= 2 (no K4 minor) by Polya/species generating functions.

Third, enumeration-free method for A362908(n) = (# K4-minor-free graphs on n unlabeled nodes) - (# forests).

Ingredients (all series in x; "p_k" means the cycle-index variable p_k evaluated at g(x^k)):
  Networks (poles 0, inf not counted; automorphisms fix both poles), simple graphs, SP only:
    N = e + P                       non-series networks (e = single edge, weight 1)
    S = sum_{k>=2} N^k p1^(k-1)     series: ordered chain of >= 2 non-series parts
    P = e*E_{>=1}(S) + E_{>=2}(S)   parallel: set of >= 2 parts, at most one real edge
  Twisted versions (sum over automorphisms that swap the two poles), marked t:
    St = p1*N(x^2)/(1-y2) + Nt*y2/(1-y2),  y2 = p2*N(x^2)  (reversal of the chain; even/odd length)
    Et = exp(St + sum_{k>=2} [k odd ? St(x^k) : S(x^k)]/k),  Pt = 2Et - 2 - St,  Nt = 1 + Pt
  Blocks B = K2 + 2-connected SP graphs, via the dissymmetry theorem on the SPQR tree (only S/P nodes):
    B2 = B_S + B_P - B_SP, with B_S = dihedral cycles with edges decorated by N, B_P = bonds with >= 3 parts,
    B_SP = an S-network and a P-network glued at a split pair.
  Connected graphs from blocks (block-cut tree dissymmetry), with B' = dB/dp1 (carried as a dual number):
    C. = x exp(sum_k B'(x^k)/k),   C = C. + B(C.) - C. B'(C.),   all graphs = Euler transform of C.
Usage: sp_gf.py NMAX   -> prints n, blocks, connected, all (tw<=2), forests, tw==2
"""
import sys
from fractions import Fraction as Fr
from math import gcd

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 16
Z = Fr(0)


def zero():
    return [Z] * (NMAX + 1)


def const(c):
    r = zero(); r[0] = Fr(c); return r


def add(*xs):
    r = zero()
    for a in xs:
        for i in range(NMAX + 1):
            r[i] += a[i]
    return r


def scal(c, a):
    return [c * v for v in a]


def mul(a, b):
    r = zero()
    for i, ai in enumerate(a):
        if ai:
            for j in range(NMAX + 1 - i):
                if b[j]:
                    r[i + j] += ai * b[j]
    return r


def subx(a, k):
    r = zero()
    for i in range(0, NMAX // k + 1):
        r[i * k] = a[i]
    return r


def exp_s(a):
    assert a[0] == 0
    e = zero(); e[0] = Fr(1)
    for n in range(1, NMAX + 1):
        e[n] = sum(k * a[k] * e[n - k] for k in range(1, n + 1)) / n
    return e


def inv1m(a):  # 1/(1-a)
    assert a[0] == 0
    r = zero(); r[0] = Fr(1)
    for n in range(1, NMAX + 1):
        r[n] = sum(a[k] * r[n - k] for k in range(1, n + 1))
    return r


def log1m(a):  # -log(1-a) = sum a^j/j
    assert a[0] == 0
    da = [i * a[i] for i in range(1, NMAX + 1)] + [Z]   # a'
    q = mul(da, inv1m(a))
    r = zero()
    for i in range(1, NMAX + 1):
        r[i] = q[i - 1] / i
    return r


class D:
    """dual number: value series v and d/dp1 series d"""
    def __init__(self, v, d=None):
        self.v = v; self.d = d if d is not None else zero()

    def __add__(self, o):
        o = o if isinstance(o, D) else D(o)
        return D(add(self.v, o.v), add(self.d, o.d))

    def __sub__(self, o):
        o = o if isinstance(o, D) else D(o)
        return D(add(self.v, scal(-1, o.v)), add(self.d, scal(-1, o.d)))

    def __mul__(self, o):
        if isinstance(o, D):
            return D(mul(self.v, o.v), add(mul(self.v, o.d), mul(self.d, o.v)))
        if isinstance(o, list):
            return D(mul(self.v, o), mul(self.d, o))
        return D(scal(Fr(o), self.v), scal(Fr(o), self.d))
    __rmul__ = __mul__


def dexp(a):
    e = exp_s(a.v); return D(e, mul(e, a.d))


def dinv1m(a):
    r = inv1m(a.v); return D(r, mul(mul(r, r), a.d))


def dlog1m(a):
    return D(log1m(a.v), mul(a.d, inv1m(a.v)))


def phi(m):
    return sum(1 for i in range(1, m + 1) if gcd(i, m) == 1)


ONE = const(1)


def step(g, st):
    """one fixed-point pass for networks + blocks given vertex weight g (plain series, g[0]=0)."""
    S, P, N, St, Pt, Nt = st
    p1 = D(g, ONE)
    p2 = subx(g, 2)
    N2 = subx(N.v, 2)
    # networks
    S = N * N * p1 * dinv1m(N * p1)
    E = dexp(S + add(*[scal(Fr(1, k), subx(S.v, k)) for k in range(2, NMAX + 1)]))
    P = 2 * E - const(2) - S
    N = D(ONE) + P
    y2 = mul(p2, N2)
    iy2 = inv1m(y2)
    St = p1 * mul(N2, iy2) + Nt * mul(y2, iy2)
    Et = dexp(St + add(*[scal(Fr(1, k), subx(St.v if k % 2 else S.v, k)) for k in range(2, NMAX + 1)]))
    Pt = 2 * Et - const(2) - St
    Nt = D(ONE) + Pt
    # blocks
    y = p1 * N
    L1 = dlog1m(y)
    rot = Fr(1, 2) * L1
    for m in range(2, NMAX + 1):
        rot = rot + D(scal(Fr(phi(m), 2 * m), subx(L1.v, m)))
    BS = rot - Fr(1, 2) * y - Fr(1, 4) * (y * y) - D(scal(Fr(1, 4), y2))
    BS = BS + Fr(1, 2) * (p1 * Nt * mul(y2, iy2)) + Fr(1, 4) * ((p1 * p1 * N2 + Nt * Nt * p2) * mul(y2, iy2))
    S2 = subx(S.v, 2)
    G = (E - ONE - S) + (E - ONE - S - Fr(1, 2) * (S * S + D(S2)))
    Gt = (Et - ONE - St) + (Et - ONE - St - Fr(1, 2) * (St * St + D(S2)))
    BP = Fr(1, 2) * (p1 * p1 * G + Gt * p2)
    BSP = Fr(1, 2) * (p1 * p1 * S * P + St * Pt * p2)
    K2 = Fr(1, 2) * (p1 * p1 + D(p2))
    B = K2 + BS + BP - BSP
    return (S, P, N, St, Pt, Nt), B


def init_state():
    z = D(zero())
    return (z, z, D(ONE), z, z, D(ONE))


def blocks_with_g(g):
    st = init_state()
    prev = None
    for _ in range(NMAX + 3):
        st, B = step(g, st)
        if prev is not None and B.v == prev.v and B.d == prev.d:
            break
        prev = B
    return st, B


def solve():
    x = zero(); x[1] = Fr(1)
    # blocks by vertex count: g = x
    _, Bx = blocks_with_g(x)
    # connected: fixed point in C. (rooted), networks iterated jointly
    Cr = x[:]
    st = init_state()
    for it in range(3 * NMAX + 10):
        st, B = step(Cr, st)
        new = mul(x, exp_s(add(*[scal(Fr(1, k), subx(B.d, k)) for k in range(1, NMAX + 1)])))
        if new == Cr and it > NMAX + 2:
            break
        Cr = new
    C = add(Cr, B.v, scal(-1, mul(Cr, B.d)))
    A = exp_s(add(*[scal(Fr(1, k), subx(C, k)) for k in range(1, NMAX + 1)]))
    return Bx.v, C, A


def forests():
    """unlabeled forests (A005195) via Otter: rooted trees R, trees T = R - (R^2 - R(x^2))/2, Euler."""
    R = zero(); R[1] = Fr(1)
    for _ in range(NMAX + 2):
        x = zero(); x[1] = Fr(1)
        R = mul(x, exp_s(add(*[scal(Fr(1, k), subx(R, k)) for k in range(1, NMAX + 1)])))
    T = add(R, scal(Fr(-1, 2), add(mul(R, R), scal(-1, subx(R, 2)))))
    return exp_s(add(*[scal(Fr(1, k), subx(T, k)) for k in range(1, NMAX + 1)]))


if __name__ == "__main__":
    B, C, A = solve()
    Fo = forests()
    print("n blocks connected_tw<=2 all_tw<=2 forests tw==2")
    for n in range(1, NMAX + 1):
        vals = [B[n], C[n], A[n], Fo[n]]
        assert all(v.denominator == 1 for v in vals), (n, vals)
        print(n, *[int(v) for v in vals], int(A[n] - Fo[n]))
