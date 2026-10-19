#!/bin/sh
# Build geng (nauty 2.9.3) with treewidth hooks -> search/bin/geng_tw
# nauty is built from the official 2.9.3 source tarball (sha256-checked) in $NAUTY_SRC (default /tmp/nauty_src).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
BIN="$ROOT/search/bin"; mkdir -p "$BIN"
SRC=${NAUTY_SRC:-/tmp/nauty_src}
TGZ="$SRC/nauty2_9_3.tar.gz"
SHA=9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b
mkdir -p "$SRC"
[ -f "$TGZ" ] || curl -sL -A "Mozilla/5.0" -o "$TGZ" https://pallini.di.uniroma1.it/nauty2_9_3.tar.gz
echo "$SHA  $TGZ" | shasum -a 256 -c -
N="$SRC/nauty2_9_3"
[ -f "$N/geng.c" ] || tar -xzf "$TGZ" -C "$SRC"
if [ ! -f "$N/gtoolsW.o" ]; then
  (cd "$N" && ./configure >/dev/null && make gtoolsW.o nautyW1.o nautilW1.o naugraphW1.o schreierW.o naurng.o >/dev/null)
fi
clang -O3 -march=native -o "$BIN/geng_tw.tmp$$" -DWORDSIZE=32 -DMAXN=WORDSIZE \
  -DPRUNE=tw_prune -DOUTPROC=tw_out -DSUMMARY=tw_summary \
  -I"$N" -I"$HERE" "$N/geng.c" "$HERE/geng_tw.c" \
  "$N/gtoolsW.o" "$N/nautyW1.o" "$N/nautilW1.o" "$N/naugraphW1.o" "$N/schreierW.o" "$N/naurng.o"
# geng_twpp: same hooks, also applied as PREPRUNE (before geng's canonicity test); faster, same output set
clang -O3 -march=native -o "$BIN/geng_twpp.tmp$$" -DWORDSIZE=32 -DMAXN=WORDSIZE \
  -DPRUNE=tw_prune -DPREPRUNE=tw_prune -DOUTPROC=tw_out -DSUMMARY=tw_summary \
  -I"$N" -I"$HERE" "$N/geng.c" "$HERE/geng_tw.c" \
  "$N/gtoolsW.o" "$N/nautyW1.o" "$N/nautilW1.o" "$N/naugraphW1.o" "$N/schreierW.o" "$N/naurng.o"
# atomic rename: processes still running the old binaries keep their inode
mv "$BIN/geng_tw.tmp$$" "$BIN/geng_tw"; mv "$BIN/geng_twpp.tmp$$" "$BIN/geng_twpp"
echo "built $BIN/geng_tw $BIN/geng_twpp"
