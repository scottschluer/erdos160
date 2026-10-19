#!/usr/bin/env python3
"""Independent checker for Erdős Problem #160 colourings.

Definition (erdosproblems.com/160): a colouring c: {1..N} -> {colours} is
valid iff every 4-term arithmetic progression a, a+d, a+2d, a+3d (d >= 1)
inside {1..N} receives at least three distinct colours. h(N) is the least
number of colours of a valid colouring; M(k) = max N with a valid
k-colouring.

A valid k-colouring of {1..N} certifies h(N) <= k, i.e. M(k) >= N.

Input: the colours c(1), ..., c(N) in order, separated by whitespace or
commas (any hashable tokens; '#' comments ignored). Alternatively one
"i c" pair per line with --pairs (every i in 1..N exactly once).

Two methods (they must agree): a direct loop over (a, d), and a numpy
vectorised pass per d. Exit codes: 0 valid, 1 invalid, 2 malformed, 3 internal.
"""

import argparse
import sys

import numpy as np


class InputError(Exception):
    pass


def read_colouring(path, pairs):
    toks = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            s = line.split("#", 1)[0].replace(",", " ").split()
            if not s:
                continue
            if pairs:
                if len(s) != 2:
                    raise InputError(f"line {lineno}: expected 'i c'")
                toks.append((lineno, s))
            else:
                toks.extend(s)
    if not pairs:
        return toks
    col = {}
    for lineno, (i, c) in toks:
        try:
            i = int(i)
        except ValueError:
            raise InputError(f"line {lineno}: bad index {i!r}")
        if i in col:
            raise InputError(f"line {lineno}: index {i} coloured twice")
        col[i] = c
    n = len(col)
    if sorted(col) != list(range(1, n + 1)):
        missing = sorted(set(range(1, max(col) + 1)) - set(col))[:10]
        raise InputError(f"indices are not exactly 1..{n}; missing e.g. {missing}")
    return [col[i] for i in range(1, n + 1)]


def bad_aps_loop(c):
    N = len(c)
    bad = []
    for d in range(1, N):
        for a in range(0, N - 3 * d):
            if len({c[a], c[a + d], c[a + 2 * d], c[a + 3 * d]}) < 3:
                bad.append((a + 1, d))
    return bad


def bad_aps_numpy(c):
    N = len(c)
    _, x = np.unique(np.array(c, dtype=object).astype(str), return_inverse=True)
    x = x.astype(np.int64)
    bad = []
    for d in range(1, (N - 1) // 3 + 1):
        m = N - 3 * d
        q = np.stack([x[j * d: j * d + m] for j in range(4)])  # (4, m)
        q.sort(axis=0)
        distinct = 1 + (q[1:] != q[:-1]).sum(axis=0)
        bad.extend((int(a) + 1, d) for a in np.flatnonzero(distinct < 3))
    return bad


def check(path, k=None, pairs=False, out=print):
    try:
        c = read_colouring(path, pairs)
    except (InputError, OSError) as e:
        out(f"MALFORMED: {e}")
        return 2
    N = len(c)
    if N == 0:
        out("MALFORMED: empty colouring")
        return 2
    used = len(set(c))
    out(f"file      : {path}")
    out(f"N         : {N}")
    out(f"colours   : {used} distinct used" + (f" (claimed k = {k})" if k else ""))
    b1 = bad_aps_loop(c)
    b2 = sorted(bad_aps_numpy(c))
    out(f"loop      : bad 4-APs = {len(b1)}")
    out(f"numpy     : bad 4-APs = {len(b2)}")
    if sorted(b1) != b2:
        out("INTERNAL ERROR: methods disagree")
        return 3
    n_aps = sum(N - 3 * d for d in range(1, (N - 1) // 3 + 1))
    out(f"4-APs     : {n_aps} checked")
    if b1:
        a, d = b1[0]
        out(f"example   : AP a={a} d={d}: colours "
            f"{[c[a - 1 + j * d] for j in range(4)]}")
        out(f"VERDICT   : INVALID — {len(b1)} 4-AP(s) with < 3 colours")
        return 1
    if k is not None and used > k:
        out(f"VERDICT   : INVALID for k={k} — uses {used} colours")
        return 1
    out(f"VERDICT   : VALID colouring of [1..{N}] with {used} colours "
        f"=> h({N}) <= {used}, M({used}) >= {N}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--k", type=int, help="claimed number of colours")
    ap.add_argument("--pairs", action="store_true", help="input is 'i c' lines")
    a = ap.parse_args(argv)
    return check(a.file, a.k, a.pairs)


if __name__ == "__main__":
    sys.exit(main())
