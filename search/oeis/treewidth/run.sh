#!/bin/sh
# Usage: run.sh N PARTS OUTDIR [ENV=VAL ...]   e.g. run.sh 12 4 results/treewidth-counts/raw/n12_K3_R TWK=3 TWDEC=R
# Extra geng flags (e.g. -c for connected only) via GENGFLAGS; binary via GENGBIN (geng_tw or geng_twpp).
# Runs geng_tw on N vertices split into PARTS res/mod pieces in parallel, one log per piece, then merges.
set -e
N=$1; PARTS=$2; OUT=$3; shift 3
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
G="$ROOT/search/bin/${GENGBIN:-geng_tw}"
mkdir -p "$OUT"
echo "N=$N PARTS=$PARTS ENV=$* GENGFLAGS=$GENGFLAGS GENGBIN=${GENGBIN:-geng_tw} start=$(date -u +%FT%TZ) host=$(hostname -s)" > "$OUT/run.txt"
i=0
while [ $i -lt "$PARTS" ]; do
  env "$@" "$G" -q $GENGFLAGS "$N" "$i/$PARTS" 2> "$OUT/part$i.log" &
  i=$((i+1))
done
wait
echo "end=$(date -u +%FT%TZ)" >> "$OUT/run.txt"
"$ROOT/.venv/bin/python" -I "$ROOT/search/oeis/treewidth/merge.py" "$OUT"
