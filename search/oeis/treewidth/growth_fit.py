"""Fit the exponential growth constant from sp_gf.py output: a(n) ~ c n^(-5/2) gamma^n.
Corrected ratios g(n) = a(n)/a(n-1) * (n/(n-1))^(5/2) are fitted as gamma + sum_j c_j/n^j over the last points.
Usage: growth_fit.py sp_gf_output.txt"""
import sys
from mpmath import mp, mpf, matrix, lu_solve
mp.dps = 40
rows = [l.split() for l in open(sys.argv[1])][1:]
for name, col in (("blocks", 1), ("connected", 2), ("all", 3)):
    S = {int(r[0]): int(r[col]) for r in rows}
    N = max(S)
    g = lambda n: mpf(S[n]) / S[n - 1] * (mpf(n) / (n - 1)) ** mpf(2.5)
    for order in (2, 3, 4):
        ns = list(range(N - order, N + 1))
        sol = lu_solve(matrix([[mpf(1) / mpf(n) ** j for j in range(order + 1)] for n in ns]), matrix([g(n) for n in ns]))
        print(f"{name:9s} fit order {order}: gamma ~ {mp.nstr(sol[0], 10)}")
