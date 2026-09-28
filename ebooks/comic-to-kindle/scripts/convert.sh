#!/usr/bin/env bash
# comic-to-kindle: convert CBZ/CBR/CB7/PDF (or image folders) for an e-reader with kcc-c2e.
#
# Usage:
#   convert.sh -p PROFILE [-m] [-f FORMAT] [-o OUTDIR] [-a AUTHOR] [--lang xx-XX] INPUT... [-- extra kcc-c2e flags]
#
#   -p PROFILE  KCC device profile (KO, KPW5, K11, KoC, ...). See references/device-profiles.md.
#   -m          manga: right-to-left reading and spread splitting.
#   -f FORMAT   MOBI | EPUB | MOBI+EPUB | CBZ | PDF | KFX. Default: MOBI+EPUB for Kindle when kindlegen
#               is present, EPUB otherwise; EPUB (kepub) for Kobo; PDF for reMarkable.
#   -o OUTDIR   output directory. Default: <parent of first input>/converted
#   INPUT       files, or directories (every .cbz/.cbr/.cb7/.pdf inside, sorted, up to 2 levels deep).
#   --          everything after it is passed to kcc-c2e verbatim (e.g. -- --ts 190 -r 1).
#
# Outputs that already exist are skipped, so a batch can be resumed after an interruption.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

PROFILE=""; MANGA=""; FORMAT=""; OUT=""; AUTHOR=""; LANGUAGE=""
INPUTS=(); EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    -p) PROFILE="$2"; shift 2 ;;
    -m) MANGA="-m"; shift ;;
    -f) FORMAT="$2"; shift 2 ;;
    -o) OUT="$2"; shift 2 ;;
    -a) AUTHOR="$2"; shift 2 ;;
    --lang) LANGUAGE="$2"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    --) shift; EXTRA=("$@"); break ;;
    *) INPUTS+=("$1"); shift ;;
  esac
done

[ -n "$PROFILE" ] || { echo "error: -p PROFILE is required (e.g. -p KO for a Kindle Oasis 2/3)"; exit 1; }
[ "${#INPUTS[@]}" -gt 0 ] || { echo "error: no input given"; exit 1; }
command -v kcc-c2e >/dev/null 2>&1 || { echo "error: kcc-c2e not found; run scripts/setup.sh"; exit 1; }

# kcc-c2e starts by deleting every KCC-* folder in the temp directory, so two conversions
# sharing /tmp silently corrupt each other (missing pages, truncated EPUB). Each invocation
# of this script therefore gets a private temp directory.
TMPROOT="$(mktemp -d "${TMPDIR:-/tmp}/c2k.XXXXXX")"
export TMPDIR="$TMPROOT"
trap 'rm -rf "$TMPROOT"' EXIT

# kindlegen may be on PATH yet unable to run (Rosetta missing, quarantine); test it for real.
# Captured into a variable rather than piped: grep -q closing the pipe early would make a
# healthy kindlegen look broken under pipefail.
kindlegen_works() {
  command -v kindlegen >/dev/null 2>&1 || return 1
  local out; out="$(kindlegen 2>&1 || true)"
  [[ "$out" == *"Amazon kindlegen"* ]]
}

# Default format follows the device family and what the machine can build.
if [ -z "$FORMAT" ]; then
  case "$PROFILE" in
    Ko*)   FORMAT="EPUB" ;;
    Rmk*)  FORMAT="PDF" ;;
    OTHER) FORMAT="EPUB" ;;
    *)
      if kindlegen_works; then
        FORMAT="MOBI+EPUB"
      else
        FORMAT="EPUB"
        echo "note: kindlegen missing or not runnable, producing EPUB only (deliver via Send to Kindle)."
      fi ;;
  esac
elif [[ "$FORMAT" == *MOBI* ]] && ! kindlegen_works; then
  echo "error: $FORMAT needs kindlegen and it is missing or not runnable; run scripts/setup.sh --check"; exit 1
fi

# Expand directories into archive lists.
FILES=()
for item in "${INPUTS[@]}"; do
  if [ -d "$item" ]; then
    while IFS= read -r f; do FILES+=("$f"); done < <(
      find "$item" -maxdepth 2 -type f \( -iname '*.cbz' -o -iname '*.cbr' -o -iname '*.cb7' -o -iname '*.pdf' \) | sort
    )
  elif [ -f "$item" ]; then
    FILES+=("$item")
  else
    echo "warning: skipping missing input: $item"
  fi
done
[ "${#FILES[@]}" -gt 0 ] || { echo "error: no .cbz/.cbr/.cb7/.pdf found"; exit 1; }

[ -n "$OUT" ] || OUT="$(cd "$(dirname "${FILES[0]}")" && pwd)/converted"
mkdir -p "$OUT"
echo "profile=$PROFILE format=$FORMAT manga=${MANGA:-no} files=${#FILES[@]} out=$OUT"

# Which output names prove a file is already done?
done_already() {
  local stem="$1"
  case "$FORMAT" in
    MOBI)      [ -f "$OUT/$stem.mobi" ] ;;
    EPUB)      [ -f "$OUT/$stem.epub" ] || [ -f "$OUT/$stem.kepub.epub" ] ;;
    MOBI+EPUB) [ -f "$OUT/$stem.mobi" ] && [ -f "$OUT/$stem.epub" ] ;;
    CBZ)       [ -f "$OUT/$stem.cbz" ] ;;
    PDF)       [ -f "$OUT/$stem.pdf" ] ;;
    *)         [ -n "$(find "$OUT" -maxdepth 1 -name "$stem.*" -print -quit)" ] ;;
  esac
}

OKC=0; SKIP=0; FAIL=0; FAILED=()
for f in "${FILES[@]}"; do
  base="$(basename "$f")"; stem="${base%.*}"
  if done_already "$stem"; then
    echo "skip  $base (already converted)"; SKIP=$((SKIP+1)); continue
  fi
  SECONDS=0
  echo "start $base"
  if kcc-c2e -p "$PROFILE" ${MANGA:+$MANGA} -u -f "$FORMAT" \
       ${AUTHOR:+-a "$AUTHOR"} ${LANGUAGE:+--language "$LANGUAGE"} \
       -o "$OUT" ${EXTRA[@]+"${EXTRA[@]}"} "$f" >"$OUT/.$stem.log" 2>&1; then
    echo "done  $base (${SECONDS}s)"; OKC=$((OKC+1)); rm -f "$OUT/.$stem.log"
  else
    echo "FAIL  $base (see $OUT/.$stem.log)"; FAIL=$((FAIL+1)); FAILED+=("$base")
    tail -5 "$OUT/.$stem.log" | sed 's/^/      /'
    # A failed run can leave a truncated file behind; drop it so the resume logic
    # does not mistake it for a finished volume next time.
    rm -f "$OUT/$stem.mobi" "$OUT/$stem.epub" "$OUT/$stem.kepub.epub" "$OUT/$stem.cbz" "$OUT/$stem.pdf"
  fi
done

echo "converted=$OKC skipped=$SKIP failed=$FAIL -> $OUT"
[ "$FAIL" = 0 ] || { printf 'failed: %s\n' "${FAILED[@]}"; exit 1; }
