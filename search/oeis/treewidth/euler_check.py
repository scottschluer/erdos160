"""Consistency check: totals of tw<=k graphs must equal the Euler transform of the connected tw<=k counts.

tw of a disjoint union is the max over components, so the class {tw <= k} is closed under disjoint unions and
components; hence (all graphs with tw<=k) = multisets of (connected graphs with tw<=k).
Usage: euler_check.py CONN_DIR_GLOB TOTAL_DIR_GLOB K
  where each dir holds a summary.json from merge.py (connected runs: geng -c; total runs: no -c).
"""
import glob, json, sys


def euler_transform(c):
    """c[1..N] connected counts -> a[0..N] totals (a[0]=1)."""
    N = len(c) - 1
    b = [0] * (N + 1)
    for n in range(1, N + 1):
        b[n] = sum(d * c[d] for d in range(1, n + 1) if n % d == 0)
    a = [1] + [0] * N
    for n in range(1, N + 1):
        a[n] = sum(b[k] * a[n - k] for k in range(1, n + 1))
        assert a[n] % n == 0
        a[n] //= n
    return a


def load(pattern, k):
    out = {}
    for f in glob.glob(pattern + "/summary.json"):
        s = json.load(open(f))
        out[s["n"]] = sum(v for t, v in s["tw_counts"].items() if int(t) <= k)
    return out


if __name__ == "__main__":
    conn, tot, k = load(sys.argv[1], int(sys.argv[3])), load(sys.argv[2], int(sys.argv[3])), int(sys.argv[3])
    N = max(conn)
    assert sorted(conn) == list(range(1, N + 1)), f"need connected counts for n=1..{N}, have {sorted(conn)}"
    a = euler_transform([0] + [conn[n] for n in range(1, N + 1)])
    ok = True
    for n in sorted(tot):
        if n <= N:
            flag = "OK" if a[n] == tot[n] else "MISMATCH"
            ok &= a[n] == tot[n]
            print(f"n={n:2d} connected={conn[n]} total={tot[n]} euler={a[n]} {flag}")
    sys.exit(0 if ok else 1)
