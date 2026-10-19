#!/bin/sh
# Build vera's treewidth tools against a nauty 2.9.3 source tree that has had
# `./configure && make geng` run in it (for the object files).
#   NAUTY=/path/to/nauty2_9_3 verify/treewidth/build.sh [OUTDIR]
# nauty2_9_3.tar.gz sha256 9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
if [ -z "$NAUTY" ]; then "$HERE/../build_deps.sh" > /dev/null; NAUTY="$HERE/../deps/nauty2_9_3"; fi
OUT=${1:-$HERE/bin}
mkdir -p "$OUT"
CFLAGS="-O3 -march=native -Wall -Wno-unused-function"
clang $CFLAGS -o "$OUT/twtool" "$HERE/twtool.c"
OBJS="gtoolsW.o nautyW1.o nautilW1.o naugraphW1.o schreierW.o naurng.o"
clang $CFLAGS -w -o "$OUT/vgeng" -I"$NAUTY" -I"$HERE" -DMAXN=WORDSIZE -DWORDSIZE=32 \
    -DOUTPROC=vera_out -DPRUNE=vera_prune -DSUMMARY=vera_summary \
    "$NAUTY/geng.c" "$HERE/vgeng_hook.c" $(for o in $OBJS; do echo "$NAUTY/$o"; done)
echo "built $OUT/twtool $OUT/vgeng"
