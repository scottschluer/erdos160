/* Exact treewidth for small graphs (n <= 32), adjacency as uint32 bitmasks (bit j of adj[i] = edge ij).
 *
 * Decider A (tw_le): Bodlaender, Fomin, Koster, Kratsch, Thilikos, "On exact algorithms for treewidth" (2006).
 *   tw(G) <= k  iff  the vertices can be ordered v1..vn with |Q(S_i, v_i)| <= k for all i, where S_i = {v1..v_{i-1}}
 *   and Q(S,v) = vertices outside S u {v} reachable from v by a path whose internal vertices lie in S.
 *   We DFS over eliminated sets S (memoised: the set of feasible S does not depend on the order).
 * Decider C (sp_reducible): tw(G) <= 2 iff G has no K4 minor iff G reduces to the empty graph by repeatedly
 *   deleting vertices of degree <= 1 and suppressing vertices of degree 2 (simple graph: parallel edges merge).
 */
#ifndef TW_H
#define TW_H
#include <stdint.h>
#include <string.h>

typedef uint32_t set_t;
#define POP(x) __builtin_popcount(x)
#define LOWBIT(x) __builtin_ctz(x)

/* memo: one stamp per subset; a subset is "seen" iff memo[S] == stamp */
#define TW_MAXMEMO_N 16
static uint32_t tw_memo[1u << TW_MAXMEMO_N];
static uint32_t tw_stamp = 0;

static inline set_t tw_qset(const set_t *adj, set_t S, int v) {
    set_t comp = 1u << v, frontier = 1u << v, nb = 0;
    while (frontier) {
        set_t f = frontier, newnb = 0;
        while (f) { int u = LOWBIT(f); f &= f - 1; newnb |= adj[u]; }
        nb |= newnb;
        frontier = newnb & S & ~comp;
        comp |= frontier;
    }
    return nb & ~S & ~(1u << v);
}

static int tw_dfs(const set_t *adj, int n, int k, set_t S, int nS) {
    if (n - nS <= k + 1) return 1;
    tw_memo[S] = tw_stamp;
    set_t rest = ((n == 32) ? ~0u : ((1u << n) - 1)) & ~S;
    while (rest) {
        int v = LOWBIT(rest); rest &= rest - 1;
        set_t S2 = S | (1u << v);
        if (tw_memo[S2] == tw_stamp) continue;
        if (POP(tw_qset(adj, S, v)) <= k && tw_dfs(adj, n, k, S2, nS + 1)) return 1;
    }
    return 0;
}

static inline int tw_degeneracy(const set_t *adj, int n) {
    set_t alive = (n == 32) ? ~0u : ((1u << n) - 1);
    int best = 0;
    for (int it = 0; it < n; it++) {
        int mv = -1, md = 99;
        for (set_t a = alive; a; a &= a - 1) {
            int v = LOWBIT(a), d = POP(adj[v] & alive);
            if (d < md) { md = d; mv = v; }
        }
        if (md > best) best = md;
        alive &= ~(1u << mv);
    }
    return best;
}

static inline int tw_nedges(const set_t *adj, int n) {
    int e = 0;
    for (int i = 0; i < n; i++) e += POP(adj[i]);
    return e / 2;
}

/* tw(G) <= k ? (n <= TW_MAXMEMO_N) */
static int tw_le(const set_t *adj, int n, int k) {
    if (k < 0) return n == 0;
    if (n <= k + 1) return 1;
    if (tw_nedges(adj, n) > k * n - k * (k + 1) / 2) return 0;
    if (tw_degeneracy(adj, n) > k) return 0;
    if (++tw_stamp == 0) { memset(tw_memo, 0, sizeof tw_memo); tw_stamp = 1; }
    return tw_dfs(adj, n, k, 0, 0);
}

/* Decider R: tw(G) <= k via safe reductions, falling back to tw_le on the reduced graph.
 * Rules (each preserves "tw <= k" in both directions for k >= 2):
 *   deg(v) <= 1: delete v.
 *   deg(v) <= k and N(v) minus some vertex w is a clique (v simplicial or almost simplicial): eliminate v
 *   (delete v, make N(v) a clique). G' = G/vw is a minor of G, and tw(G) <= max(deg v, tw(G')).
 * Degree-2 vertices are always almost simplicial, so for k = 2 this is exactly series-parallel reduction. */
static int tw_le_reduce(const set_t *adj0, int n, int k) {
    if (k < 2) return tw_le(adj0, n, k);
    set_t adj[32];
    memcpy(adj, adj0, n * sizeof(set_t));
    set_t alive = (n == 32) ? ~0u : ((1u << n) - 1);
    int changed = 1;
    while (changed && POP(alive) > k + 1) {
        changed = 0;
        for (set_t a = alive; a; a &= a - 1) {
            int v = LOWBIT(a);
            set_t N = adj[v] & alive;
            int d = POP(N);
            if (d > k) continue;
            int ok = (d <= 1);
            if (!ok) {
                /* almost simplicial: some w in N with N \ {w} a clique */
                for (set_t c = N; c && !ok; c &= c - 1) {
                    int w = LOWBIT(c);
                    set_t C = N & ~(1u << w);
                    int clique = 1;
                    for (set_t b = C; b && clique; b &= b - 1) { int u = LOWBIT(b); if ((adj[u] & C) != (C & ~(1u << u))) clique = 0; }
                    ok = clique;
                }
            }
            if (ok) {
                for (set_t b = N; b; b &= b - 1) { int u = LOWBIT(b); adj[u] |= N & ~(1u << u); }
                alive &= ~(1u << v);
                changed = 1;
                if (POP(alive) <= k + 1) break;
            }
        }
    }
    int m = POP(alive);
    if (m <= k + 1) return 1;
    /* relabel the reduced graph compactly and decide exactly */
    int idx[32], vs[32], t = 0;
    for (set_t a = alive; a; a &= a - 1) { int v = LOWBIT(a); idx[v] = t; vs[t++] = v; }
    set_t radj[32];
    for (int i = 0; i < m; i++) {
        set_t r = 0;
        for (set_t b = adj[vs[i]] & alive; b; b &= b - 1) r |= 1u << idx[LOWBIT(b)];
        radj[i] = r;
    }
    return tw_le(radj, m, k);
}

/* upper bound: min-fill elimination heuristic on an explicit fill graph */
static int tw_upper_minfill(const set_t *adj0, int n) {
    set_t adj[32];
    memcpy(adj, adj0, n * sizeof(set_t));
    set_t alive = (n == 32) ? ~0u : ((1u << n) - 1);
    int width = 0;
    for (int it = 0; it < n; it++) {
        int bv = -1, bfill = 1 << 30, bdeg = 99;
        for (set_t a = alive; a; a &= a - 1) {
            int v = LOWBIT(a);
            set_t N = adj[v] & alive;
            int fill = 0;
            for (set_t b = N; b; b &= b - 1) { int u = LOWBIT(b); fill += POP(N & ~adj[u] & ~(1u << u)); }
            int d = POP(N);
            if (fill < bfill || (fill == bfill && d < bdeg)) { bfill = fill; bdeg = d; bv = v; }
        }
        set_t N = adj[bv] & alive;
        if (POP(N) > width) width = POP(N);
        for (set_t b = N; b; b &= b - 1) { int u = LOWBIT(b); adj[u] |= N & ~(1u << u); }
        alive &= ~(1u << bv);
    }
    return width;
}

/* exact treewidth */
static int tw_exact(const set_t *adj, int n) {
    if (n == 0) return -1;
    int lo = tw_degeneracy(adj, n), hi = tw_upper_minfill(adj, n);
    for (int k = lo; k < hi; k++) if (tw_le(adj, n, k)) return k;
    return hi;
}

/* Decider C: series-parallel reduction; returns 1 iff tw <= 2 */
static int sp_reducible(const set_t *adj0, int n) {
    set_t adj[32];
    memcpy(adj, adj0, n * sizeof(set_t));
    set_t alive = (n == 32) ? ~0u : ((1u << n) - 1);
    int changed = 1;
    while (alive && changed) {
        changed = 0;
        for (set_t a = alive; a; a &= a - 1) {
            int v = LOWBIT(a);
            set_t N = adj[v] & alive;
            int d = POP(N);
            if (d <= 1) {
                alive &= ~(1u << v);
                changed = 1;
            } else if (d == 2) {
                int x = LOWBIT(N), y = LOWBIT(N & (N - 1));
                adj[x] |= 1u << y; adj[y] |= 1u << x;
                alive &= ~(1u << v);
                changed = 1;
            }
        }
    }
    return alive == 0;
}

/* forest test: tw <= 1 iff no cycle iff each component has |E| = |V| - 1 */
static int is_forest(const set_t *adj, int n) {
    set_t all = (n == 32) ? ~0u : ((1u << n) - 1), seen = 0;
    while (seen != all) {
        int s = LOWBIT(all & ~seen);
        set_t comp = 1u << s, fr = comp;
        while (fr) {
            set_t nb = 0;
            for (set_t f = fr; f; f &= f - 1) nb |= adj[LOWBIT(f)];
            fr = nb & ~comp; comp |= fr;
        }
        int e = 0;
        for (set_t c = comp; c; c &= c - 1) e += POP(adj[LOWBIT(c)] & comp);
        if (e / 2 != POP(comp) - 1) return 0;
        seen |= comp;
    }
    return 1;
}
#endif
