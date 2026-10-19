#!/usr/bin/env python3
"""Enumerate all valid k-colourings of {1..N} for Erdős #160 (every 4-AP
gets >= 3 colours) by plain backtracking, no SAT.

Colourings are enumerated up to colour permutation via value precedence
(colour j+1 first appears after colour j); each such colouring is the unique
representative of its permutation class. Classes are then merged under
reversal i -> N+1-i (reverse, then re-normalise colours by first use).

Usage: h160_enum.py N K [--list]
Prints: #classes up to permutation, #classes up to permutation+reversal.
"""

import argparse
import sys

import numpy as np
from numba import njit


@njit(cache=True)
def _enum(N, k, maxout):
    c = np.full(N, -1, dtype=np.int64)
    out = np.empty((maxout, N), dtype=np.int64)
    nout = 0
    total = 0
    i = 0
    used = np.zeros(N + 1, dtype=np.int64)  # used[i] = #colours used in c[0..i-1]
    while i >= 0:
        if i == N:
            if nout < maxout:
                out[nout] = c
                nout += 1
            total += 1
            i -= 1
            continue
        # next candidate colour for position i
        nxt = c[i] + 1
        lim = min(used[i] + 1, k)  # value precedence: at most one new colour
        placed = False
        while nxt < lim:
            ok = True
            # all 4-APs ending at i: i-3d, i-2d, i-d, i
            d = 1
            while i - 3 * d >= 0:
                a0 = c[i - 3 * d]
                a1 = c[i - 2 * d]
                a2 = c[i - d]
                a3 = nxt
                # count distinct among 4
                nd = 1
                if a1 != a0:
                    nd += 1
                if a2 != a0 and a2 != a1:
                    nd += 1
                if a3 != a0 and a3 != a1 and a3 != a2:
                    nd += 1
                if nd < 3:
                    ok = False
                    break
                d += 1
            if ok:
                placed = True
                break
            nxt += 1
        if placed:
            c[i] = nxt
            used[i + 1] = used[i] + (1 if nxt == used[i] else 0)
            i += 1
            if i < N:
                c[i] = -1
        else:
            c[i] = -1
            i -= 1
    return total, out[:nout]


def normalise(col):
    m = {}
    return tuple(m.setdefault(x, len(m)) for x in col)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("k", type=int)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    total, sols = _enum(a.N, a.k, 1_000_000)
    if total > len(sols):
        print(f"too many solutions to list ({total})")
        return 1
    reps = {tuple(map(int, s)) for s in sols}
    assert len(reps) == total
    orbits = set()
    for s in reps:
        orbits.add(min(s, normalise(s[::-1])))
    print(f"N={a.N} k={a.k}: {total} colourings up to colour permutation "
          f"(using <= {a.k} colours); {len(orbits)} up to permutation+reversal")
    if a.list:
        for s in sorted(orbits):
            print(" ".join(map(str, s)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
