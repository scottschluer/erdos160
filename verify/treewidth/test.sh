#!/bin/sh
# Regression test for vera's treewidth tools: reproduce OEIS A263294 rows
# n=1..9 (data as of 2026-10-18) with unpruned geng + exact tw, and the
# tw<=2 / tw<=3 partial sums with every pruner. Needs build.sh first.
set -e
B=$(cd "$(dirname "$0")" && pwd)/bin
fail=0
check() {  # label expected actual
    if [ "$2" = "$3" ]; then echo "ok   $1: $3"; else echo "FAIL $1: want '$2' got '$3'"; fail=1; fi
}
hist() { sed -n 's/.*mismatches=0 hist: //p'; }
set -- \
  "1:1" "2:1 1" "3:1 2 1" "4:1 5 4 1" "5:1 9 17 6 1" "6:1 19 72 53 10 1" \
  "7:1 36 323 501 168 14 1" "8:1 75 1639 5889 4163 557 21 1" \
  "9:1 152 9203 81786 138923 42596 1977 29 1"
for row in "$@"; do
    n=${row%%:*}; want=${row#*:}
    check "row n=$n" "$want" "$("$B/vgeng" -q "$n" 2>&1 | hist)"
    # pruned runs must give the same leading columns, zeros after
    set -- $want
    w2="$1 ${2:-0} ${3:-0}"; w3="$w2 ${4:-0}"
    for dec in elim sp; do
        got=$(VERA_K=2 VERA_DEC=$dec "$B/vgeng" -q "$n" 2>&1 | hist | cut -d' ' -f1-3)
        [ "$n" -lt 3 ] && got=$(echo "$got 0 0" | cut -d' ' -f1-3)
        check "n=$n tw<=2 ($dec)" "$w2" "$got"
    done
    for dec in elim ap; do
        got=$(VERA_K=3 VERA_DEC=$dec "$B/vgeng" -q "$n" 2>&1 | hist | cut -d' ' -f1-4)
        [ "$n" -lt 4 ] && got=$(echo "$got 0 0 0" | cut -d' ' -f1-4)
        check "n=$n tw<=3 ($dec)" "$w3" "$got"
    done
done
# twtool on a few hand-made graph6 strings: K4 (tw 3), C5 (tw 2), K5 (tw 4),
# octahedron K2,2,2 (tw 4), path P4 (tw 1), empty graph on 3 vertices (tw 0)
check "twtool" "3 2 4 4 1 0" "$(printf 'C~\nDhc\nD~{\nE}lw\nCh\nB?\n' | "$B/twtool" -p 2>/dev/null | cut -d' ' -f1 | tr '\n' ' ' | sed 's/ $//')"
[ $fail = 0 ] && echo "all treewidth tests passed" || { echo "TREEWIDTH TESTS FAILED"; exit 1; }
