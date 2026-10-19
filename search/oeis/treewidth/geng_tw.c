/* geng hooks: count unlabeled graphs by exact treewidth (and edge count).
 *
 * Linked into nauty's geng.c with -DPRUNE=tw_prune -DOUTPROC=tw_out -DSUMMARY=tw_summary.
 * Environment:
 *   TWK=k     prune every intermediate graph with tw > k (tw <= k is hereditary, so this is exact).
 *             Unset or negative: no pruning (all graphs are generated).
 *   TWCAP=c   in OUTPROC, graphs with degeneracy > c are tallied as "tw > c" without computing tw exactly.
 *   TWDEC=A|R decider used by PRUNE and for classifying outputs when pruning:
 *             A = pure Q-set DFS (tw_le), R = safe reductions + DFS fallback (tw_le_reduce). Default R.
 *             Unpruned runs always classify with tw_exact (degeneracy/min-fill bounds + tw_le).
 *   TWCHECK=1 cross-check: tw <= 1 vs forest test, tw <= 2 vs series-parallel reduction, and (when
 *             pruning) the classification vs tw_exact.
 * Output (stderr): one line per (tw, edges) cell: "TWE n tw e count", then "TW n tw count" totals.
 */
#include "gtools.h"
#include "tw.h"
#include <stdlib.h>

static int K = -2, CAP = 99, CHECK = 0, DEC_R = 1;
static unsigned long long cnt[34][34 * 33 / 2 + 1];
static unsigned long long over_cap, mismatches, nprune_calls;
static int maxn_seen = 0;

static void init_env(void) {
    const char *s;
    K = (s = getenv("TWK")) ? atoi(s) : -1;
    CAP = (s = getenv("TWCAP")) ? atoi(s) : 99;
    CHECK = (s = getenv("TWCHECK")) ? atoi(s) : 0;
    DEC_R = !((s = getenv("TWDEC")) && s[0] == 'A');
}

static inline int decide(const set_t *adj, int n, int k) {
    return DEC_R ? tw_le_reduce(adj, n, k) : tw_le(adj, n, k);
}

/* exact tw of a graph known to have tw <= K */
static int classify(const set_t *adj, int n) {
    if (tw_nedges(adj, n) == 0) return 0;
    if (is_forest(adj, n)) return 1;
    for (int t = 2; t < K; t++) if (decide(adj, n, t)) return t;
    return K;
}

static inline void to_adj(graph *g, int n, set_t *adj) {
    for (int i = 0; i < n; i++) adj[i] = __builtin_bitreverse32((uint32_t)g[i]) & ((n == 32) ? ~0u : ((1u << n) - 1));
}

int tw_prune(graph *g, int n, int maxn) {
    if (K == -2) init_env();
    if (K < 0) return 0;
    nprune_calls++;
    set_t adj[32];
    to_adj(g, n, adj);
    int v = n - 1;
    set_t N = adj[v];
    int d = POP(N);
    if (d <= 1) return 0;                       /* adding a leaf/isolated vertex never raises tw above 1 */
    if (d <= K) {                               /* simplicial new vertex of degree <= K keeps tw <= K */
        int clique = 1;
        for (set_t b = N; b && clique; b &= b - 1) { int u = LOWBIT(b); if ((adj[u] & N) != (N & ~(1u << u))) clique = 0; }
        if (clique) return 0;
    }
    return !decide(adj, n, K);
}

void tw_out(FILE *f, graph *g, int n) {
    if (K == -2) init_env();
    set_t adj[32];
    to_adj(g, n, adj);
    int e = tw_nedges(adj, n);
    if (n > maxn_seen) maxn_seen = n;
    if (tw_degeneracy(adj, n) > CAP) { over_cap++; return; }
    int t = (K >= 0) ? classify(adj, n) : tw_exact(adj, n);
    if (CHECK) {
        if (K >= 0 && t != tw_exact(adj, n)) mismatches++;
        if ((t <= 2) != sp_reducible(adj, n)) mismatches++;
        if ((t <= 1) != is_forest(adj, n)) mismatches++;
    }
    cnt[t][e]++;
}

void tw_summary(nauty_counter nout, double cpu) {
    int n = maxn_seen;
    unsigned long long tot[34] = {0};
    for (int t = 0; t < 34; t++)
        for (int e = 0; e <= 34 * 33 / 2; e++)
            if (cnt[t][e]) { fprintf(stderr, "TWE %d %d %d %llu\n", n, t, e, cnt[t][e]); tot[t] += cnt[t][e]; }
    for (int t = 0; t < 34; t++) if (tot[t]) fprintf(stderr, "TW %d %d %llu\n", n, t, tot[t]);
    if (over_cap) fprintf(stderr, "TWOVERCAP %d %d %llu\n", n, CAP, over_cap);
    fprintf(stderr, "TWINFO n=%d K=%d DEC=%c CAP=%d CHECK=%d nout=%llu prune_calls=%llu mismatches=%llu cpu=%.2f\n",
            n, K, DEC_R ? 'R' : 'A', CAP, CHECK, (unsigned long long)nout, nprune_calls, mismatches, cpu);
}
