/* Independent treewidth deciders (vera). Written from definitions only; does
 * not use anything from search/.
 *
 * Graphs: n <= 24 vertices, adjacency as bitmasks adj[i] (bit j = edge ij).
 *
 *   tw_elim_le(n, adj, k)  tw(G) <= k ?  Elimination game on the fill graph:
 *       tw(G) <= k iff the vertices can be eliminated one by one, each having
 *       <= k neighbours at elimination time, where eliminating v turns N(v)
 *       into a clique. The graph after eliminating a set S does not depend on
 *       the order, so DFS over S is memoised on S. Safe shortcuts: eliminate
 *       a simplicial vertex of degree <= k without branching; fail if the
 *       current graph has degeneracy > k.
 *   tw_exact(n, adj)       smallest k with tw_elim_le, from degeneracy up.
 *   tw_sp_le2(n, adj)      tw <= 2 by series-parallel reduction (delete
 *       deg <= 1, suppress deg 2). No search.
 *   tw_ap_le3(n, adj)      tw <= 3 by Arnborg-Proskurowski reduction rules
 *       (deg<=1, series, triangle, buddy, cube). No search.
 */
#ifndef VERA_TW_H
#define VERA_TW_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef uint32_t vset;
#define VBIT(i) ((vset)1u << (i))
#define VPOP(x) __builtin_popcount(x)
#define VCTZ(x) __builtin_ctz(x)
#define VMAXN 24

static inline vset vall(int n) { return n >= 32 ? ~(vset)0 : VBIT(n) - 1; }

/* ------------------------------------------------------------ helpers */

static int degeneracy(int n, const vset *adj, vset R)
{
    vset g[VMAXN];
    for (int i = 0; i < n; i++) g[i] = adj[i] & R;
    int best = 0;
    while (R) {
        int v = -1, dv = 99;
        for (vset r = R; r; r &= r - 1) {
            int u = VCTZ(r), d = VPOP(g[u] & R);
            if (d < dv) { dv = d; v = u; }
        }
        if (dv > best) best = dv;
        R &= ~VBIT(v);
    }
    return best;
}

static inline int is_clique(const vset *g, vset s)
{
    for (vset r = s; r; r &= r - 1) {
        int u = VCTZ(r);
        if ((g[u] & s) != (s & ~VBIT(u))) return 0;
    }
    return 1;
}

/* ---------------------------------------------------- elimination game */

static uint32_t *el_stamp = NULL;
static uint32_t el_cur = 0;
static int el_alloc_n = -1;
static int el_k;

static void el_prepare(int n)
{
    if (n > el_alloc_n) {
        free(el_stamp);
        el_stamp = (uint32_t *)calloc((size_t)1 << n, sizeof(uint32_t));
        el_alloc_n = n;
        el_cur = 0;
    }
    if (++el_cur == 0) {
        memset(el_stamp, 0, ((size_t)1 << el_alloc_n) * sizeof(uint32_t));
        el_cur = 1;
    }
}

/* g: fill graph on R = V \ S (rows outside R are ignored). */
static int el_dfs(vset S, vset R, const vset *g)
{
    int rem = VPOP(R);
    if (rem <= el_k + 1) return 1;
    /* forced move: simplicial vertex of degree <= k */
    for (vset r = R; r; r &= r - 1) {
        int v = VCTZ(r);
        vset nb = g[v];
        if (VPOP(nb) <= el_k && is_clique(g, nb)) {
            vset T = S | VBIT(v);
            if (el_stamp[T] == el_cur) return 0;
            el_stamp[T] = el_cur;
            vset h[VMAXN];
            memcpy(h, g, sizeof(h));
            for (vset q = nb; q; q &= q - 1) h[VCTZ(q)] &= ~VBIT(v);
            return el_dfs(T, R & ~VBIT(v), h);
        }
    }
    if (degeneracy(VMAXN, g, R) > el_k) return 0;
    for (vset r = R; r; r &= r - 1) {
        int v = VCTZ(r);
        vset nb = g[v];
        if (VPOP(nb) > el_k) continue;
        vset T = S | VBIT(v);
        if (el_stamp[T] == el_cur) continue;
        el_stamp[T] = el_cur;
        vset h[VMAXN];
        memcpy(h, g, sizeof(h));
        for (vset q = nb; q; q &= q - 1) {
            int u = VCTZ(q);
            h[u] = (h[u] | nb) & ~VBIT(u) & ~VBIT(v);
        }
        if (el_dfs(T, R & ~VBIT(v), h)) return 1;
    }
    return 0;
}

static int tw_elim_le(int n, const vset *adj, int k)
{
    if (k < 0) return n == 0;
    if (n <= k + 1) return 1;
    el_prepare(n);
    el_k = k;
    vset g[VMAXN] = {0};
    for (int i = 0; i < n; i++) g[i] = adj[i];
    el_stamp[0] = el_cur;
    return el_dfs(0, vall(n), g);
}

static int tw_exact(int n, const vset *adj)
{
    if (n == 0) return -1;
    int k = degeneracy(n, adj, vall(n));
    while (!tw_elim_le(n, adj, k)) k++;
    return k;
}

/* ------------------------------------------- series-parallel (tw <= 2) */

static int tw_sp_le2(int n, const vset *adj)
{
    vset g[VMAXN];
    for (int i = 0; i < n; i++) g[i] = adj[i];
    vset R = vall(n);
    int changed = 1;
    while (R && changed) {
        changed = 0;
        for (vset r = R; r; r &= r - 1) {
            int v = VCTZ(r);
            vset nb = g[v];
            int d = VPOP(nb);
            if (d > 2) continue;
            for (vset q = nb; q; q &= q - 1) g[VCTZ(q)] &= ~VBIT(v);
            if (d == 2) {
                int a = VCTZ(nb), b = VCTZ(nb & (nb - 1));
                g[a] |= VBIT(b);
                g[b] |= VBIT(a);
            }
            g[v] = 0;
            R &= ~VBIT(v);
            changed = 1;
        }
    }
    return R == 0;
}

/* ------------------------------- Arnborg-Proskurowski rules (tw <= 3) */

static inline void ap_remove(vset *g, vset *R, int v)
{
    for (vset q = g[v]; q; q &= q - 1) g[VCTZ(q)] &= ~VBIT(v);
    g[v] = 0;
    *R &= ~VBIT(v);
}

static inline void ap_make_clique(vset *g, vset s)
{
    for (vset q = s; q; q &= q - 1) {
        int u = VCTZ(q);
        g[u] |= s & ~VBIT(u);
    }
}

/* one rule application; returns 1 if something was reduced */
static int ap_step(vset *g, vset *R)
{
    /* rules 1-3: degree <= 1; degree 2 (series); degree 3 with an edge
       among its neighbours (triangle). All are eliminations of v. */
    for (vset r = *R; r; r &= r - 1) {
        int v = VCTZ(r);
        vset nb = g[v];
        int d = VPOP(nb);
        int has_edge = 0;
        if (d == 3)
            for (vset q = nb; q; q &= q - 1)
                if (g[VCTZ(q)] & nb) has_edge = 1;
        if (d <= 2 || (d == 3 && has_edge)) {
            ap_remove(g, R, v);
            if (d >= 2) ap_make_clique(g, nb);
            return 1;
        }
    }
    /* rule 4 (buddy): v, w of degree 3 with the same independent nbhd */
    for (vset r = *R; r; r &= r - 1) {
        int v = VCTZ(r);
        if (VPOP(g[v]) != 3) continue;
        for (vset s = r & (r - 1); s; s &= s - 1) {
            int w = VCTZ(s);
            if (g[w] == g[v]) {
                vset nb = g[v];
                ap_remove(g, R, v);
                ap_remove(g, R, w);
                ap_make_clique(g, nb);
                return 1;
            }
        }
    }
    /* rule 5 (cube): v, w, x of degree 3, distinct a, b, c, d with
       N(v) = {a,b,d}, N(w) = {b,c,d}, N(x) = {a,c,d}; replace by K4 on abcd */
    for (vset r = *R; r; r &= r - 1) {
        int v = VCTZ(r);
        vset nv = g[v];
        if (VPOP(nv) != 3) continue;
        for (vset q = nv; q; q &= q - 1) {
            int d = VCTZ(q);
            vset ab = nv & ~VBIT(d);
            int a0 = VCTZ(ab), b0 = VCTZ(ab & (ab - 1));
            for (int swap = 0; swap < 2; swap++) {
                int a = swap ? b0 : a0, b = swap ? a0 : b0;
                for (vset s = *R & ~VBIT(v); s; s &= s - 1) {
                    int w = VCTZ(s);
                    vset nw = g[w];
                    if (VPOP(nw) != 3) continue;
                    if ((nw & (VBIT(b) | VBIT(d))) != (VBIT(b) | VBIT(d))) continue;
                    if (nw & VBIT(a)) continue;
                    int c = VCTZ(nw & ~(VBIT(b) | VBIT(d)));
                    if (c == v || c == w) continue;
                    vset want = VBIT(a) | VBIT(c) | VBIT(d);
                    for (vset t = *R & ~(VBIT(v) | VBIT(w)); t; t &= t - 1) {
                        int x = VCTZ(t);
                        if (g[x] != want) continue;
                        vset abcd = VBIT(a) | VBIT(b) | VBIT(c) | VBIT(d);
                        if ((VBIT(v) | VBIT(w) | VBIT(x)) & abcd) continue;
                        ap_remove(g, R, v);
                        ap_remove(g, R, w);
                        ap_remove(g, R, x);
                        ap_make_clique(g, abcd);
                        return 1;
                    }
                }
            }
        }
    }
    return 0;
}

static int tw_ap_le3(int n, const vset *adj)
{
    vset g[VMAXN];
    for (int i = 0; i < n; i++) g[i] = adj[i];
    vset R = vall(n);
    while (R && ap_step(g, &R)) {}
    return R == 0;
}

#endif
