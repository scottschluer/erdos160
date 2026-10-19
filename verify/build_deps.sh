#!/bin/sh
# Fetch and build vera's external tools into verify/deps/ (gitignored), pinned:
#   nauty 2.9.3   tarball sha256 9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b
#   drat-trim     github.com/marijnheule/drat-trim @ 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 (drat-trim, lrat-check)
# Needs network, clang, git. cadical is taken from PATH (tested with 3.0.1).
# Idempotent: skips anything already built.
set -e
D=$(cd "$(dirname "$0")" && pwd)/deps
mkdir -p "$D"
NAUTY_SHA=9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b
DRAT_COMMIT=2e3b2dc0ecf938addbd779d42877b6ed69d9a985

if [ ! -x "$D/drat-trim/drat-trim" ] || [ ! -x "$D/drat-trim/lrat-check" ]; then
    rm -rf "$D/drat-trim"
    git clone -q https://github.com/marijnheule/drat-trim.git "$D/drat-trim"
    git -C "$D/drat-trim" checkout -q "$DRAT_COMMIT"
    clang -O2 -o "$D/drat-trim/drat-trim" "$D/drat-trim/drat-trim.c"
    clang -O2 -o "$D/drat-trim/lrat-check" "$D/drat-trim/lrat-check.c"
fi
echo "drat-trim: $D/drat-trim/drat-trim, $D/drat-trim/lrat-check @ $(git -C "$D/drat-trim" rev-parse --short HEAD)"

if [ ! -f "$D/nauty2_9_3/gtoolsW.o" ]; then
    T="$D/nauty2_9_3.tar.gz"
    [ -f "$T" ] || curl -sL -m 300 -o "$T" https://pallini.di.uniroma1.it/nauty2_9_3.tar.gz
    got=$(shasum -a 256 "$T" | cut -d' ' -f1)
    if [ "$got" != "$NAUTY_SHA" ]; then echo "nauty sha256 mismatch: $got" >&2; exit 1; fi
    (cd "$D" && tar xzf nauty2_9_3.tar.gz)
    (cd "$D/nauty2_9_3" && ./configure --quiet > /dev/null 2>&1 && make geng > /dev/null 2>&1)
fi
echo "nauty:     $D/nauty2_9_3 (sha256 ok)"
