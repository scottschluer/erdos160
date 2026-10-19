"""Incremental conquer: one CaDiCaL instance per worker process, cubes passed as assumptions so learnt
clauses (all implied by the base CNF) carry over between cubes. Contiguous chunks keep neighbouring,
similar cubes on the same solver. No proofs — this is for finding the answer fast; certification is a
separate per-cube DRAT re-solve.

Usage: python inc_conquer.py base.cnf cubes.icnf results.tsv [--jobs 4] [--chunk 200] [--range A B]
Appends 'idx<TAB>UNSAT|SAT<TAB>seconds' to results.tsv, skipping cubes already listed there.
SAT cubes also get the model written to results.tsv.model_<idx>.
"""
import argparse, os, time
from multiprocessing import Pool

S = None


def init(cnf):
    global S
    from pysat.formula import CNF
    from pysat.solvers import Solver
    S = Solver(name="cadical195", bootstrap_with=CNF(from_file=cnf).clauses)


def work(chunk):
    out = []
    for i, cube in chunk:
        t = time.time()
        r = S.solve(assumptions=cube)
        out.append((i, "SAT" if r else "UNSAT", time.time() - t, S.get_model() if r else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf"); ap.add_argument("cubes"); ap.add_argument("results")
    ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--chunk", type=int, default=200)
    ap.add_argument("--range", type=int, nargs=2, default=None, help="only cubes with A <= idx < B")
    a = ap.parse_args()
    cubes = [[int(t) for t in l.split()[1:] if t != "0"] for l in open(a.cubes) if l.startswith("a")]
    done = set()
    if os.path.exists(a.results):
        done = {int(l.split()[0]) for l in open(a.results) if l.strip()}
    todo = [(i, c) for i, c in enumerate(cubes) if i not in done and (not a.range or a.range[0] <= i < a.range[1])]
    chunks = [todo[j:j + a.chunk] for j in range(0, len(todo), a.chunk)]
    print(f"{len(todo)} cubes left in {len(chunks)} chunks", flush=True)
    with open(a.results, "a") as f, Pool(a.jobs, initializer=init, initargs=(a.cnf,)) as pool:
        for res in pool.imap_unordered(work, chunks):
            for i, st, el, model in res:
                f.write(f"{i}\t{st}\t{el:.2f}\n")
                if model:
                    open(f"{a.results}.model_{i}", "w").write(" ".join(map(str, model)) + "\n")
                    print(f"SAT cube {i}", flush=True)
            f.flush()


if __name__ == "__main__":
    main()
