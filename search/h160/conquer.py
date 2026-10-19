"""Conquer cubes from march_cu: for each cube (line 'a l1 l2 ... 0'), solve CNF + cube units with kissat.

Usage: python conquer.py base.cnf cubes.icnf outdir [--jobs 4] [--sample n --seed s] [--time T] [--proof]
Writes outdir/results.tsv: cube_index, status (UNSAT/SAT/UNKNOWN), seconds. With --proof, keeps
outdir/proofs/<idx>.drat (DRAT for base + cube units). Resumable: cubes already in results.tsv are skipped.
"""
import argparse, os, random, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor


def read_cubes(path):
    cubes = []
    for line in open(path):
        if line.startswith("a"):
            cubes.append([int(t) for t in line.split()[1:] if t != "0"])
    return cubes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf"); ap.add_argument("cubes"); ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--time", type=int, default=0)
    ap.add_argument("--proof", action="store_true")
    a = ap.parse_args()
    lines = open(a.cnf).read().splitlines()
    hdr = next(i for i, l in enumerate(lines) if l.startswith("p cnf"))
    nv, nc = map(int, lines[hdr].split()[2:4])
    body = "\n".join(l for l in lines[hdr + 1:] if l and not l.startswith("c")) + "\n"
    cubes = read_cubes(a.cubes)
    idx = list(range(len(cubes)))
    if a.sample:
        random.Random(a.seed).shuffle(idx); idx = sorted(idx[:a.sample])
    os.makedirs(a.outdir, exist_ok=True)
    if a.proof:
        os.makedirs(os.path.join(a.outdir, "proofs"), exist_ok=True)
    resf = os.path.join(a.outdir, "results.tsv")
    done = set()
    if os.path.exists(resf):
        done = {int(l.split()[0]) for l in open(resf) if l.strip()}
    idx = [i for i in idx if i not in done]
    out = open(resf, "a")

    def solve(i):
        cube = cubes[i]
        with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False, dir="/tmp") as f:
            f.write(f"p cnf {nv} {nc + len(cube)}\n"); f.write(body)
            f.write("".join(f"{l} 0\n" for l in cube)); fn = f.name
        cmd = ["kissat", "-q", fn]
        if a.time:
            cmd.insert(2, f"--time={a.time}")
        if a.proof:
            cmd += [os.path.join(a.outdir, "proofs", f"{i}.drat"), "--no-binary"]
        t = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        el = time.time() - t
        os.unlink(fn)
        st = "SAT" if p.returncode == 10 else "UNSAT" if p.returncode == 20 else "UNKNOWN"
        model = ""
        if st == "SAT":
            model = " ".join(l[2:] for l in p.stdout.splitlines() if l.startswith("v "))
        return i, st, el, model

    with ThreadPoolExecutor(a.jobs) as ex:
        for i, st, el, model in ex.map(solve, idx):
            out.write(f"{i}\t{st}\t{el:.2f}\n"); out.flush()
            if st == "SAT":
                open(os.path.join(a.outdir, f"model_{i}.txt"), "w").write(model + "\n")
                print(f"SAT cube {i}", flush=True)


if __name__ == "__main__":
    main()
