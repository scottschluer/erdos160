#!/usr/bin/env python3
"""Check a cube-and-conquer UNSAT certificate.

F is UNSAT if (1) the cubes cover every assignment, i.e. the CNF made of the
negations of all cubes is UNSAT, and (2) F AND cube_i is UNSAT for every i.

  (1) is proved here from scratch: write {-cube_i}, solve with cadical
      writing DRAT, check with drat-trim.
  (2) each cube needs a DRAT proof of F + units(cube_i). With --proofs DIR the
      proof for cube i (0-based, in file order) is DIR/cube<i>.drat;
      otherwise this script solves F + units(cube_i) with cadical itself and
      checks the proof it writes (an independent re-solve).

Cube file: march_cu format, lines "a l1 l2 ... 0".

  --lrat           re-solve with `cadical --lrat` and check with lrat-check
                   (much faster to check than DRAT via drat-trim).
  --no-coverage    skip (1): for symmetry-reduced cube sets, where coverage
                   holds only up to symmetry and is argued separately.
  --log FILE       append "i<TAB>OK|FAIL<TAB>seconds" per cube; cubes already
                   logged OK are skipped on restart.

Usage: cnc_check.py F.cnf CUBES.icnf [--proofs DIR] [--lrat] [--no-coverage]
                    [--jobs J] [--work DIR] [--log FILE]
Exit 0 iff everything checked verifies.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

lock = threading.Lock()

_DEPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deps")  # verify/build_deps.sh
DRAT_TRIM = os.environ.get("DRAT_TRIM", os.path.join(_DEPS, "drat-trim", "drat-trim"))
CADICAL = os.environ.get("CADICAL", "cadical")
LRAT_CHECK = os.environ.get("LRAT_CHECK", os.path.join(_DEPS, "drat-trim", "lrat-check"))


def read_cnf(path):
    nv, cl, cur = 0, [], []
    with open(path) as f:
        for line in f:
            if line.startswith(("c", "%")):
                continue
            if line.startswith("p"):
                nv = int(line.split()[2])
                continue
            for t in line.split():
                v = int(t)
                if v == 0:
                    cl.append(cur)
                    cur = []
                else:
                    cur.append(v)
    return nv, cl


def read_cubes(path):
    cubes = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            s = line.split()
            if not s or s[0] != "a":
                continue
            lits = [int(t) for t in s[1:]]
            if lits[-1] != 0:
                raise ValueError(f"cube line {lineno} not 0-terminated")
            cubes.append(lits[:-1])
    return cubes


def write_cnf(path, nv, clauses):
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")


def drat_ok(cnf, proof):
    r = subprocess.run([DRAT_TRIM, cnf, proof], capture_output=True, text=True)
    out = r.stdout.replace("\r", "")
    return any(l.strip() == "s VERIFIED" for l in out.splitlines()), out


def lrat_ok(cnf, proof):
    r = subprocess.run([LRAT_CHECK, cnf, proof], capture_output=True, text=True)
    out = (r.stdout + r.stderr).replace("\r", "")
    return any(l.strip() == "c VERIFIED" for l in out.splitlines()), out


def solve_and_check(cnf, proof, lrat=False):
    cmd = [CADICAL, "-q", "--no-binary"] + (["--lrat"] if lrat else []) + [cnf, proof]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 20:
        return False, f"cadical returned {r.returncode} (20 = UNSAT expected)"
    return lrat_ok(cnf, proof) if lrat else drat_ok(cnf, proof)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cnf")
    ap.add_argument("cubes")
    ap.add_argument("--proofs")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--work")
    ap.add_argument("--lrat", action="store_true")
    ap.add_argument("--no-coverage", action="store_true")
    ap.add_argument("--log")
    a = ap.parse_args()
    nv, F = read_cnf(a.cnf)
    cubes = read_cubes(a.cubes)
    work = a.work or tempfile.mkdtemp(prefix="vera_cnc_")
    os.makedirs(work, exist_ok=True)
    print(f"formula: {nv} vars, {len(F)} clauses; cubes: {len(cubes)}; work: {work}")
    for c in cubes:
        if any(abs(l) > nv for l in c) or len({abs(l) for l in c}) != len(c):
            print(f"BAD CUBE (out of range or repeated variable): {c}")
            return 1
    # (1) coverage
    if a.no_coverage:
        print("coverage: NOT CHECKED HERE (--no-coverage; must be argued separately)")
    else:
        cov = os.path.join(work, "coverage.cnf")
        write_cnf(cov, nv, [[-l for l in c] for c in cubes])
        ok, out = solve_and_check(cov, os.path.join(work, "coverage.drat"))
        print(f"coverage (negated cubes UNSAT): {'VERIFIED' if ok else 'FAILED'}")
        if not ok:
            print(out[-2000:])
            return 1
    done = set()
    if a.log and os.path.exists(a.log):
        with open(a.log) as f:
            for line in f:
                t = line.split()
                if len(t) >= 2 and t[1] == "OK":
                    done.add(int(t[0]))
        print(f"resume: {len(done)} cubes already verified in {a.log}")
    logf = open(a.log, "a") if a.log else None
    ext = "lrat" if a.lrat else "drat"

    # (2) every cube
    def one(i):
        if i in done:
            return i, True, ""
        t0 = time.time()
        fc = os.path.join(work, f"F_cube{i}.cnf")
        write_cnf(fc, nv, F + [[l] for l in cubes[i]])
        if a.proofs:
            ok, out = drat_ok(fc, os.path.join(a.proofs, f"cube{i}.drat"))
        else:
            ok, out = solve_and_check(fc, os.path.join(work, f"cube{i}.{ext}"), a.lrat)
        if ok:
            os.remove(fc)
            p = os.path.join(work, f"cube{i}.{ext}")
            if not a.proofs and os.path.exists(p):
                os.remove(p)
        if logf:
            with lock:
                logf.write(f"{i}\t{'OK' if ok else 'FAIL'}\t{time.time() - t0:.2f}\n")
                logf.flush()
        return i, ok, out

    bad = []
    with ThreadPoolExecutor(a.jobs) as ex:
        for n_done, (i, ok, out) in enumerate(ex.map(one, range(len(cubes))), 1):
            if not ok:
                bad.append(i)
                print(f"cube {i}: FAILED\n{out[-1000:]}")
            if n_done % 100 == 0:
                print(f"  {n_done}/{len(cubes)} cubes checked, {len(bad)} failed", flush=True)
    if bad:
        print(f"VERDICT: NOT VERIFIED — {len(bad)} cube(s) failed: {bad[:20]}")
        return 1
    what = "all" if a.no_coverage else "coverage + all"
    print(f"VERDICT: VERIFIED — {what} {len(cubes)} cubes UNSAT with checked "
          f"{'LRAT' if a.lrat else 'DRAT'}" + (" (coverage argued separately)" if a.no_coverage else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
