/* twtool: read graph6 graphs on stdin, compute exact treewidth with the
 * elimination game and cross-check the independent tw<=2 (series-parallel)
 * and tw<=3 (Arnborg-Proskurowski) deciders on every graph.
 *
 *   twtool            histogram of tw by n, plus mismatch counts
 *   twtool -p         also print "tw graph6" per graph
 *
 * Build: clang -O3 -march=native -o twtool twtool.c
 */
#include <stdio.h>
#include "tw.h"

static int parse_g6(const char *s, int *n, vset *adj)
{
    if (*s == '>') return -1;           /* header >>graph6<< not supported */
    int nn = *s++ - 63;
    if (nn < 0 || nn > VMAXN) return -1;
    *n = nn;
    for (int i = 0; i < nn; i++) adj[i] = 0;
    int k = 0, x = 0;
    for (int j = 1; j < nn; j++)
        for (int i = 0; i < j; i++) {
            if (k == 0) {
                if (*s < 63 || *s > 126) return -1;
                x = *s++ - 63;
                k = 6;
            }
            k--;
            if (x >> k & 1) { adj[i] |= VBIT(j); adj[j] |= VBIT(i); }
        }
    return 0;
}

int main(int argc, char **argv)
{
    int print = argc > 1 && argv[1][0] == '-' && argv[1][1] == 'p';
    static long long hist[VMAXN + 1][VMAXN + 1];
    long long bad_sp = 0, bad_ap = 0, total = 0;
    char line[256];
    int maxn = 0;
    while (fgets(line, sizeof line, stdin)) {
        int n;
        vset adj[VMAXN];
        if (parse_g6(line, &n, adj)) { fprintf(stderr, "bad line: %s", line); return 2; }
        int tw = tw_exact(n, adj);
        int sp = tw_sp_le2(n, adj), ap = tw_ap_le3(n, adj);
        if (sp != (tw <= 2)) {
            if (bad_sp++ < 5) fprintf(stderr, "SP MISMATCH tw=%d sp=%d %s", tw, sp, line);
        }
        if (ap != (tw <= 3)) {
            if (bad_ap++ < 5) fprintf(stderr, "AP MISMATCH tw=%d ap=%d %s", tw, ap, line);
        }
        if (print) printf("%d %s", tw, line);
        hist[n][tw < 0 ? 0 : tw]++;
        if (n > maxn) maxn = n;
        total++;
    }
    for (int n = 0; n <= maxn; n++) {
        long long s = 0;
        for (int k = 0; k <= VMAXN; k++) s += hist[n][k];
        if (!s) continue;
        fprintf(stderr, "n=%d total=%lld row:", n, s);
        for (int k = 0; k < (n > 0 ? n : 1); k++) fprintf(stderr, " %lld", hist[n][k]);
        fprintf(stderr, "\n");
    }
    fprintf(stderr, "graphs=%lld sp_mismatch=%lld ap_mismatch=%lld\n", total, bad_sp, bad_ap);
    return (bad_sp || bad_ap) ? 1 : 0;
}
