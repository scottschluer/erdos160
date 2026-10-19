#!/usr/bin/env python3
"""Tests for h160_coloring.py and h160_cnf.py.

Brute force over all colourings for small N is compared with both checker
methods and with SAT on the CNF (with and without --sb).

Run: .venv/bin/python verify/test_h160.py
"""

import os
import sys
import tempfile
from itertools import product

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h160_cnf as hc  # noqa: E402
import h160_coloring as hcol  # noqa: E402
from pysat.solvers import Cadical153  # noqa: E402


def write(tokens):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(" ".join(map(str, tokens)) + "\n")
    f.close()
    return f.name


def run(tokens, **kw):
    out = []
    code = hcol.check(write(tokens), out=out.append, **kw)
    return code, "\n".join(out)


def brute_exists(N, k):
    """Is there a valid k-colouring of [N]? Exhaustive, numpy."""
    if N < 4:
        return True
    C = np.array(list(product(range(k), repeat=N)), dtype=np.int8)
    ok = np.ones(len(C), dtype=bool)
    for d in range(1, (N - 1) // 3 + 1):
        for a in range(N - 3 * d):
            q = np.sort(C[:, [a, a + d, a + 2 * d, a + 3 * d]], axis=1)
            distinct = 1 + (q[:, 1:] != q[:, :-1]).sum(axis=1)
            ok &= distinct >= 3
    return bool(ok.any())


def sat(N, k, sb):
    nv, cl = hc.clauses(N, k, sb)
    with Cadical153(bootstrap_with=cl) as s:
        if s.solve():
            return hc.decode(s.get_model(), N, k)
        return None


def test_checker_basic():
    # 1..N all distinct colours: valid
    assert run(list(range(10)))[0] == 0
    # constant colouring with N >= 4: invalid
    code, out = run([1] * 7)
    assert code == 1 and "INVALID" in out, out
    # N < 4: no APs, anything valid
    assert run(["a", "a", "a"])[0] == 0
    # exactly-2-colour AP: 1,2,1,2 invalid
    code, out = run([1, 2, 1, 2])
    assert code == 1, out
    # 3 colours on an AP fine
    assert run([1, 2, 3, 1])[0] == 0
    # claimed k smaller than used
    assert run([1, 2, 3, 4], k=3)[0] == 1
    # pairs format, shuffled
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write("3 c\n1 a\n2 b\n4 a\n")
    f.close()
    out = []
    assert hcol.check(f.name, pairs=True, out=out.append) == 0, out
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write("1 a\n3 b\n")
    f.close()
    assert hcol.check(f.name, pairs=True, out=lambda s: None) == 2
    assert run([])[0] == 2


def test_methods_agree_random(trials=500):
    rng = np.random.default_rng(7)
    for _ in range(trials):
        N = int(rng.integers(1, 60))
        k = int(rng.integers(1, 7))
        c = rng.integers(0, k, size=N).tolist()
        assert sorted(hcol.bad_aps_loop(c)) == sorted(hcol.bad_aps_numpy(c))


def test_brute_vs_sat():
    for k in (2, 3):
        for N in range(1, 14 if k == 3 else 9):
            want = brute_exists(N, k)
            for sb in (False, True):
                col = sat(N, k, sb)
                assert (col is not None) == want, (N, k, sb, want)
                if col is not None:
                    assert hcol.bad_aps_loop(col) == [], (N, k, col)
    # M(3) = 12 by brute force
    assert brute_exists(12, 3) and not brute_exists(13, 3)


def test_known_small_M():
    # remy's/hal's claimed M(4) = 22: check with my encoding
    for sb in (False, True):
        assert sat(22, 4, sb) is not None
        assert sat(23, 4, sb) is None


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("all h160 tests passed")
