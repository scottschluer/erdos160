/* geng hooks (vera): PRUNE by an independent tw<=k decider, and an OUTPROC
 * that histograms exact treewidth of every output graph while cross-checking
 * all deciders against each other.
 *
 * Environment:
 *   VERA_K    prune threshold k (unset/negative: no pruning)
 *   VERA_DEC  prune decider: elim (default) | sp (k=2 only) | ap (k=3 only)
 *
 * PRUNE is sound because treewidth never increases on induced subgraphs and
 * geng's intermediate graphs are induced subgraphs of the output graph.
 *
 * On exit (SUMMARY) prints to stderr:
 *   VERA n=<n> k=<k> dec=<d> out=<count> mismatches=<m> hist: h0 h1 ...
 * where h_j = number of output graphs with treewidth j (n=0 graph: -1 -> h0).
 */
#include "gtools.h"
#include "tw.h"

static int v_init = 0, v_k = -1, v_dec = 0, v_n = 0;
static long long v_hist[VMAXN + 1];
static long long v_mism = 0;

static void v_setup(void)
{
    if (v_init) return;
    v_init = 1;
    const char *k = getenv("VERA_K"), *d = getenv("VERA_DEC");
    v_k = k ? atoi(k) : -1;
    if (d && !strcmp(d, "sp")) v_dec = 1;
    else if (d && !strcmp(d, "ap")) v_dec = 2;
    if ((v_dec == 1 && v_k != 2) || (v_dec == 2 && v_k != 3)) {
        fprintf(stderr, "VERA_DEC=%s needs VERA_K=%d\n", d, v_dec + 1);
        exit(2);
    }
}

static inline void v_adj(graph *g, int n, vset *adj)
{
#if WORDSIZE != 32
#error build with -DWORDSIZE=32
#endif
    for (int i = 0; i < n; i++) adj[i] = __builtin_bitreverse32((uint32_t)g[i]);
}

int vera_prune(graph *g, int n, int maxn)
{
    v_setup();
    if (v_k < 0) return 0;
    vset adj[VMAXN];
    v_adj(g, n, adj);
    int ok = v_dec == 1 ? tw_sp_le2(n, adj)
           : v_dec == 2 ? tw_ap_le3(n, adj)
           : tw_elim_le(n, adj, v_k);
    return !ok;
}

void vera_out(FILE *f, graph *g, int n)
{
    v_setup();
    vset adj[VMAXN];
    v_adj(g, n, adj);
    int tw = tw_exact(n, adj);
    v_hist[tw < 0 ? 0 : tw]++;
    v_n = n;
    int bad = 0;
    if (tw_sp_le2(n, adj) != (tw <= 2)) bad = 1;
    if (tw_ap_le3(n, adj) != (tw <= 3)) bad = 1;
    if (v_k >= 0 && tw > v_k) bad = 1;
    if (bad && v_mism++ < 5) {
        fprintf(stderr, "VERA MISMATCH n=%d tw=%d sp=%d ap=%d adj:", n, tw,
                tw_sp_le2(n, adj), tw_ap_le3(n, adj));
        for (int i = 0; i < n; i++) fprintf(stderr, " %x", adj[i]);
        fprintf(stderr, "\n");
    }
}

void vera_summary(nauty_counter nout, double cpu)
{
    static const char *dn[] = {"elim", "sp", "ap"};
    long long s = 0;
    for (int j = 0; j <= VMAXN; j++) s += v_hist[j];
    fprintf(stderr, "VERA n=%d k=%d dec=%s out=%llu hist_total=%lld cpu=%.1f "
            "mismatches=%lld hist:", v_n, v_k, dn[v_dec],
            (unsigned long long)nout, s, cpu, v_mism);
    for (int j = 0; j < (v_n > 0 ? v_n : 1); j++) fprintf(stderr, " %lld", v_hist[j]);
    fprintf(stderr, "\n");
}
