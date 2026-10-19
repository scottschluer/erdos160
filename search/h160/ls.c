// ls.c — tabu search for Erdős #160 colourings: colour [1..N] with k colours so that every
// 4-term AP gets >= 3 distinct colours. Cost = number of 4-APs with <= 2 colours.
// Move: recolour one vertex of a random bad AP to the best non-tabu colour (aspiration on new best).
// On success at N, extends to N+1 by appending a random colour and continues.
//
// Usage: ls k N0 [-s seed] [-t seconds] [-o prefix] [-i init]   writes <prefix>_k<k>_N<N>.txt (one colour per line)
// -i: warm start from a file of whitespace-separated colours c(1)..c(n); positions n+1..N0 are random.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 4096
static int N, K;
static int col[MAXN + 1];
static int nap;                 // APs as (a,d)
static int *apa, *apd;
static int *inc, *incs;         // vertex -> list of APs containing it (CSR)
static int bad[1 << 22], bpos[1 << 22], nbad;
static uint64_t rs = 88172645463325252ULL;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static inline int ncol4(int a, int b, int c, int d) {
  int n = 1;
  if (b != a) n++;
  if (c != a && c != b) n++;
  if (d != a && d != b && d != c) n++;
  return n;
}
static inline int isbad(int q) {
  int a = apa[q], d = apd[q];
  return ncol4(col[a], col[a + d], col[a + 2 * d], col[a + 3 * d]) <= 2;
}
static void build(void) {
  nap = 0;
  for (int d = 1; 3 * d < N; d++) for (int a = 1; a + 3 * d <= N; a++) nap++;
  free(apa); free(apd); free(inc); free(incs);
  apa = malloc(nap * sizeof(int)); apd = malloc(nap * sizeof(int));
  int q = 0; int *cnt = calloc(N + 2, sizeof(int));
  for (int d = 1; 3 * d < N; d++) for (int a = 1; a + 3 * d <= N; a++) {
    apa[q] = a; apd[q] = d; q++;
    for (int j = 0; j < 4; j++) cnt[a + j * d]++;
  }
  incs = malloc((N + 2) * sizeof(int)); incs[1] = 0;
  for (int i = 1; i <= N; i++) incs[i + 1] = incs[i] + cnt[i];
  inc = malloc(incs[N + 1] * sizeof(int));
  memset(cnt, 0, (N + 2) * sizeof(int));
  for (q = 0; q < nap; q++) for (int j = 0; j < 4; j++) { int v = apa[q] + j * apd[q]; inc[incs[v] + cnt[v]++] = q; }
  free(cnt);
  nbad = 0;
  for (q = 0; q < nap; q++) { bpos[q] = -1; if (isbad(q)) { bpos[q] = nbad; bad[nbad++] = q; } }
}
static inline void setbad(int q, int b) {
  if (b && bpos[q] < 0) { bpos[q] = nbad; bad[nbad++] = q; }
  else if (!b && bpos[q] >= 0) { int i = bpos[q], l = bad[--nbad]; bad[i] = l; bpos[l] = i; bpos[q] = -1; }
}
static int delta(int v, int c) {  // change in cost if v recoloured to c
  int old = col[v], d = 0;
  for (int e = incs[v]; e < incs[v + 1]; e++) {
    int q = inc[e]; int b0 = bpos[q] >= 0;
    col[v] = c; int b1 = isbad(q); col[v] = old;
    d += b1 - b0;
  }
  return d;
}
static void recolour(int v, int c) {
  col[v] = c;
  for (int e = incs[v]; e < incs[v + 1]; e++) setbad(inc[e], isbad(inc[e]));
}
static void save(const char *prefix) {
  char fn[512]; snprintf(fn, sizeof fn, "%s_k%d_N%d.txt", prefix, K, N);
  FILE *f = fopen(fn, "w");
  for (int i = 1; i <= N; i++) fprintf(f, "%d\n", col[i]);
  fclose(f);
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: ls k N0 [-s seed] [-t secs] [-o prefix]\n"); return 1; }
  K = atoi(argv[1]); N = atoi(argv[2]);
  double tlim = 60; const char *prefix = "h160", *init = NULL;
  for (int a = 3; a < argc; a++) {
    if (!strcmp(argv[a], "-s")) rs = strtoull(argv[++a], 0, 10) * 2654435761ULL + 1;
    else if (!strcmp(argv[a], "-t")) tlim = atof(argv[++a]);
    else if (!strcmp(argv[a], "-o")) prefix = argv[++a];
    else if (!strcmp(argv[a], "-i")) init = argv[++a];
  }
  for (int i = 1; i <= MAXN; i++) col[i] = rnd() % K;
  if (init) {
    FILE *f = fopen(init, "r"); int n = 0, c;
    while (n < MAXN && fscanf(f, "%d", &c) == 1) col[++n] = c;
    fclose(f);
    if (n > N) N = n;
  }
  static long tabu[MAXN + 1][64];
  struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
  build();
  long it = 0; int best = nbad;
  for (;;) {
    if (nbad == 0) {
      clock_gettime(CLOCK_MONOTONIC, &t1);
      double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
      printf("k=%d N=%d FOUND it=%ld t=%.1fs\n", K, N, it, el); fflush(stdout);
      save(prefix);
      if (N >= MAXN) break;
      N++; col[N] = rnd() % K; build(); best = nbad;
      memset(tabu, 0, sizeof tabu); it = 0;
      continue;
    }
    if ((it & 4095) == 0) {
      clock_gettime(CLOCK_MONOTONIC, &t1);
      if ((t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec) > tlim) break;
    }
    it++;
    int q = bad[rnd() % nbad];
    int bv = -1, bc = -1, bd = 1 << 30, ties = 0;
    for (int j = 0; j < 4; j++) {
      int v = apa[q] + j * apd[q];
      for (int c = 0; c < K; c++) {
        if (c == col[v]) continue;
        int d = delta(v, c);
        int ok = tabu[v][c] <= it || nbad + d < best;
        if (!ok) continue;
        if (d < bd) { bd = d; bv = v; bc = c; ties = 1; }
        else if (d == bd && rnd() % ++ties == 0) { bv = v; bc = c; }
      }
    }
    if (bv < 0) continue;
    int oldc = col[bv];
    recolour(bv, bc);
    tabu[bv][oldc] = it + 5 + rnd() % 10;
    if (nbad < best) best = nbad;
  }
  printf("k=%d N=%d STOP best=%d it=%ld\n", K, N, best, it);
  return 0;
}
