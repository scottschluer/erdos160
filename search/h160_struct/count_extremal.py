"""Enumerate all valid k-colourings of [N] (every 4-AP gets >= 3 distinct colours), up to colour
permutation (value precedence) and report them up to reversal too. Direct x-only CNF, blocking clauses.
usage: count_extremal.py N K [limit]"""
import sys, itertools
from pysat.solvers import Cadical153

def solve_all(N, K, limit=10**6):
    var = lambda i, c: i * K + c + 1          # i in 0..N-1
    cl = []
    for i in range(N):
        cl.append([var(i, c) for c in range(K)])
        for a, b in itertools.combinations(range(K), 2): cl.append([-var(i, a), -var(i, b)])
    forb = set()
    for d in range(1, N):
        for a in range(N - 3 * d):
            pts = (a, a + d, a + 2 * d, a + 3 * d)
            for c1, c2 in itertools.combinations_with_replacement(range(K), 2):
                for pat in itertools.product((c1, c2), repeat=4):
                    forb.add(tuple(-var(p, c) for p, c in zip(pts, pat)))
    cl += [list(f) for f in forb]
    # value precedence: colour c may appear at i only if colour c-1 appears before i
    # m[i][c] = colour c used somewhere in 0..i
    nv = N * K
    def mvar(i, c): return nv + i * K + c + 1
    for i in range(N):
        for c in range(K):
            # m(i,c) <-> m(i-1,c) or x(i,c)
            prev = [mvar(i - 1, c)] if i > 0 else []
            cl.append([-mvar(i, c), var(i, c)] + prev)
            cl.append([mvar(i, c), -var(i, c)])
            if prev: cl.append([mvar(i, c), -prev[0]])
            if c > 0:
                cl.append([-var(i, c)] + ([mvar(i - 1, c - 1)] if i > 0 else []))
    s = Cadical153(bootstrap_with=cl)
    sols = []
    while s.solve() and len(sols) < limit:
        m = s.get_model()
        col = tuple(next(c for c in range(K) if m[var(i, c) - 1] > 0) for i in range(N))
        sols.append(col)
        s.add_clause([-var(i, col[i]) for i in range(N)])
    return sols

def canon(col):
    seen = {}; out = []
    for c in col:
        if c not in seen: seen[c] = len(seen)
        out.append(seen[c])
    return tuple(out)

if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2]); lim = int(sys.argv[3]) if len(sys.argv) > 3 else 10**6
    sols = solve_all(N, K, lim)
    classes = {min(s, canon(s[::-1])) for s in sols}
    print(f"N={N} K={K}: {len(sols)} colourings up to colour permutation; {len(classes)} up to reversal too"
          + (" (LIMIT HIT)" if len(sols) >= lim else ""))
    for c in sorted(classes)[:20]:
        print(" ".join(map(str, c)), "  palindromic-up-to-perm" if canon(c[::-1]) == c else "")
