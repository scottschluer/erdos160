"""Exact h(N) for Erdos #160: min colours so every 4-term AP in [1..N] has >=3 distinct colours. Quick SAT probe (remy)."""
import sys, time
from pysat.solvers import Cadical153
def feasible(N,k):
    x=lambda i,c:(i-1)*k+c+1
    s=Cadical153()
    for i in range(1,N+1):
        s.add_clause([x(i,c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1+1,k): s.add_clause([-x(i,c1),-x(i,c2)])
    # symmetry: colour of i <= i-1 (first-use ordering)
    for i in range(1,N+1):
        for c in range(k):
            if c>i-1: s.add_clause([-x(i,c)])
    # 4-AP a,a+d,a+2d,a+3d must not use <=2 colours: forbid every pair of colours {c1,c2} covering all four
    for d in range(1,(N-1)//3+1):
        for a in range(1,N-3*d+1):
            P=[a+j*d for j in range(4)]
            for c1 in range(k):
                for c2 in range(c1,k):
                    # not all of P in {c1,c2}: clause over positions: some p has colour outside {c1,c2}
                    s.add_clause([x(p,c) for p in P for c in range(k) if c not in (c1,c2)])
    r=s.solve(); s.delete(); return r
if __name__=="__main__":
    N0,N1=int(sys.argv[1]),int(sys.argv[2]); k=3
    for N in range(N0,N1+1):
        t=time.time()
        while not feasible(N,k): k+=1
        print(N,k,round(time.time()-t,2),flush=True)
