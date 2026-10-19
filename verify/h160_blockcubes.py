#!/usr/bin/env python3
"""Independent centre-block cubes for Erdős #160 (vera).

For F = h160_cnf.py N K (no --sb), a block [lo..hi] with lo + hi = N + 1 is
mapped onto itself by the reversal i -> N+1-i. The symmetry group
S_K x <reversal> acts on valid colourings of [N] and, compatibly, on their
restrictions to the block. So F is UNSAT iff F AND (block = r) is UNSAT for one
representative r of every orbit of block colourings under that group. Block
colourings with a monochromatic-ish 4-AP inside the block can be dropped,
because F's own AP clauses refute them.

Representatives: valid block colourings in restricted-growth form (colours by
first use = canonical under S_K) that are <= the RGS form of their reversal.
They are enumerated with the backtracking enumerator from h160_enum.py (no SAT).

Usage: h160_blockcubes.py N K LO HI OUT.icnf [--compare OTHER.icnf]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h160_enum  # noqa: E402


def rgs(seq):
    m = {}
    return tuple(m.setdefault(c, len(m)) for c in seq)


def representatives(L, K):
    total, sols = h160_enum._enum(L, K, 10_000_000)
    assert total == len(sols)
    reps = set()
    for s in sols:
        s = tuple(int(c) for c in s)
        assert rgs(s) == s
        reps.add(min(s, rgs(s[::-1])))
    return total, sorted(reps)


def cube_lits(rep, lo, K):
    return [(lo + j - 1) * K + (c + 1) for j, c in enumerate(rep)]


def read_icnf(path):
    out = set()
    with open(path) as f:
        for line in f:
            s = line.split()
            if s and s[0] == "a":
                lits = [int(t) for t in s[1:] if t != "0"]
                out.add(tuple(sorted(l for l in lits if l > 0)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("N", type=int)
    ap.add_argument("K", type=int)
    ap.add_argument("lo", type=int)
    ap.add_argument("hi", type=int)
    ap.add_argument("out")
    ap.add_argument("--compare")
    a = ap.parse_args()
    if a.lo + a.hi != a.N + 1:
        sys.exit("block must be centred: lo + hi = N + 1")
    L = a.hi - a.lo + 1
    total, reps = representatives(L, a.K)
    with open(a.out, "w") as f:
        for r in reps:
            f.write("a " + " ".join(map(str, cube_lits(r, a.lo, a.K))) + " 0\n")
    print(f"block [{a.lo}..{a.hi}] (length {L}), K={a.K}: {total} valid block "
          f"colourings up to S_K, {len(reps)} up to S_K x reversal -> {a.out}")
    if a.compare:
        mine = {tuple(sorted(cube_lits(r, a.lo, a.K))) for r in reps}
        theirs = read_icnf(a.compare)
        print(f"compare: mine {len(mine)}, theirs {len(theirs)}, "
              f"missing from theirs {len(mine - theirs)}, extra in theirs {len(theirs - mine)}")
        if mine - theirs:
            print("  e.g. missing:", sorted(mine - theirs)[:3])
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
