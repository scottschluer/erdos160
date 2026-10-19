"""Cubes for Erdős #160 from colourings of a centre-symmetric block [L..R] (L+R = N+1).

Every valid k-colouring c of [1..N] is equivalent, under colour permutation and reversal i -> N+1-i, to one
whose restriction to the block B = [L..R]
  (1) is a restricted growth string (colours numbered 1,2,... by first appearance left to right in B), and
  (2) is lex <= the restricted growth string of its own reversal (reversal maps B onto itself).
So the cubes "x(i, b_i) true and x(i, c) false for c != b_i, for i in B", over all valid block colourings b
meeting (1) and (2), cover every valid colouring. Use them with a CNF that has NO other symmetry breaking.
Validity of b is checked on 4-APs inside B only (each is also a 4-AP of [1..N]).

Variables follow verify/h160_cnf.py: x(i, c) = (i-1)*k + c, i in 1..N, c in 1..k.

Usage: python block_cubes.py N k L R > cubes.icnf      (prints the count to stderr)
"""
import sys


def rgs(seq):
    m, out = {}, []
    for s in seq:
        if s not in m:
            m[s] = len(m) + 1
        out.append(m[s])
    return out


def block_colourings(m, k):
    """All valid RGS colourings of positions 0..m-1 (every 4-AP inside gets >= 3 colours)."""
    col = [0] * m
    aps = [[] for _ in range(m)]  # APs ending at position j: (a, a+d, a+2d, j)
    for j in range(m):
        for d in range(1, j // 3 + 1):
            aps[j].append((j - 3 * d, j - 2 * d, j - d))

    def ok(j):
        c = col[j]
        for a, b, e in aps[j]:
            if len({col[a], col[b], col[e], c}) <= 2:
                return False
        return True

    def rec(j, used):
        if j == m:
            yield list(col)
            return
        for c in range(1, min(used + 1, k) + 1):
            col[j] = c
            if ok(j):
                yield from rec(j + 1, max(used, c))

    yield from rec(0, 0)


def main():
    N, k, L, R = map(int, sys.argv[1:5])
    assert L + R == N + 1, "block must be centre-symmetric"
    m = R - L + 1
    n = 0
    out = sys.stdout
    for b in block_colourings(m, k):
        if b > rgs(b[::-1]):
            continue
        lits = []
        for t, c in enumerate(b):
            i = L + t
            lits += [(i - 1) * k + cc if cc == c else -((i - 1) * k + cc) for cc in range(1, k + 1)]
        out.write("a " + " ".join(map(str, lits)) + " 0\n")
        n += 1
    print(f"{n} cubes, block [{L},{R}] m={m} k={k}", file=sys.stderr)


if __name__ == "__main__":
    main()
