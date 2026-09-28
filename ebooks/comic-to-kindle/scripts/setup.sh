#!/usr/bin/env bash
# comic-to-kindle: install or check the tools the skill relies on.
#   kcc-c2e   Kindle Comic Converter CLI (resizes pages, writes fixed-layout EPUB/MOBI/KEPUB)
#   kindlegen Amazon's MOBI compiler, needed only for Kindle-over-USB output
#   RAR tool  needed to open .cbr archives
#
# Usage: setup.sh [--check]
#   --check  only report, install nothing
set -euo pipefail

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

BIN="$HOME/.local/bin"
mkdir -p "$BIN"
export PATH="$BIN:$PATH"
OS="$(uname -s)"
MISSING=0

ok()   { printf '  [ok]   %s\n' "$*"; }
miss() { printf '  [miss] %s\n' "$*"; MISSING=1; }
note() { printf '  [note] %s\n' "$*"; }

echo "== kcc-c2e =="
if command -v kcc-c2e >/dev/null 2>&1; then
  ok "$(command -v kcc-c2e)"
elif [ "$CHECK_ONLY" = 1 ]; then
  miss "not installed (run setup.sh without --check)"
else
  # KCC is not published on PyPI under a stable name: install from the GitHub repo.
  if command -v uv >/dev/null 2>&1; then
    uv tool install "git+https://github.com/ciromattia/kcc.git"
  elif command -v pipx >/dev/null 2>&1; then
    pipx install "git+https://github.com/ciromattia/kcc.git"
  else
    miss "need uv (https://docs.astral.sh/uv/) or pipx to install kcc-c2e"
    exit 1
  fi
  if command -v kcc-c2e >/dev/null 2>&1; then ok "$(command -v kcc-c2e)"; else miss "install failed"; exit 1; fi
fi

echo "== kindlegen (MOBI output, Kindle over USB) =="
if command -v kindlegen >/dev/null 2>&1; then
  ok "$(command -v kindlegen)"
else
  case "$OS" in
    Darwin)
      # Kindle Previewer bundles kindlegen. Reuse an installed Previewer if present,
      # otherwise download the pkg with Homebrew and unpack the binary: no sudo needed.
      KG="$(find /Applications -maxdepth 6 -path '*Kindle Previewer*' -name kindlegen -type f 2>/dev/null | head -1 || true)"
      if [ -z "$KG" ] && [ "$CHECK_ONLY" = 0 ] && command -v brew >/dev/null 2>&1; then
        echo "  fetching Kindle Previewer package (about 450 MB, one time)..."
        brew fetch --cask kindle-previewer >/dev/null
        PKG="$(/bin/ls -t "$(brew --cache)"/downloads/*KindlePreviewer*.pkg 2>/dev/null | head -1 || true)"
        if [ -n "$PKG" ]; then
          TMP="$(mktemp -d)"
          ( cd "$TMP" && xar -xf "$PKG" && for p in $(find . -name Payload); do gunzip -dc "$p" | cpio -id 2>/dev/null || true; done )
          KG="$(find "$TMP" -name kindlegen -type f | head -1 || true)"
        fi
      fi
      if [ -n "$KG" ]; then
        cp "$KG" "$BIN/kindlegen"
        chmod +x "$BIN/kindlegen"
        xattr -c "$BIN/kindlegen" 2>/dev/null || true
        ok "$BIN/kindlegen (extracted from Kindle Previewer)"
      elif [ "$CHECK_ONLY" = 1 ]; then
        miss "not installed (setup.sh can extract it from Kindle Previewer via Homebrew)"
      else
        miss "not found: install Homebrew, or install Kindle Previewer from Amazon and re-run"
      fi
      # kindlegen is an Intel binary; Apple Silicon runs it through Rosetta.
      if [ "$(uname -m)" = "arm64" ] && ! arch -x86_64 /usr/bin/true 2>/dev/null; then
        miss "Rosetta missing: run 'softwareupdate --install-rosetta --agree-to-license'"
      fi
      ;;
    Linux)
      note "Amazon ships kindlegen only inside Kindle Previewer (macOS/Windows)."
      note "Use EPUB output and deliver through Send to Kindle instead of MOBI."
      ;;
    *)
      note "On Windows install Kindle Previewer; kcc-c2e locates kindlegen by itself."
      ;;
  esac
fi

echo "== 7-Zip (kcc-c2e refuses any CBZ/CBR/CB7 input without it) =="
# KCC's startup check looks for '7zz' on macOS and '7z' elsewhere, whatever tool ends up extracting.
if [ "$OS" = "Darwin" ]; then SEVENZIP="7zz"; else SEVENZIP="7z"; fi
if command -v "$SEVENZIP" >/dev/null 2>&1; then
  ok "$(command -v "$SEVENZIP")"
elif [ "$CHECK_ONLY" = 0 ] && [ "$OS" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
  brew install sevenzip >/dev/null && ok "$(command -v 7zz)" || miss "brew install sevenzip failed"
else
  miss "install 7-Zip: macOS 'brew install sevenzip'; Debian/Ubuntu 'apt install p7zip-full'; Fedora 'dnf install p7zip p7zip-plugins'; Windows 7-zip.org (add to PATH)"
fi

echo "== RAR extraction for .cbr =="
if [ "$OS" = "Darwin" ]; then
  ok "bsdtar reads RAR natively (7zz is the fallback)"
elif command -v unrar >/dev/null 2>&1 || command -v unar >/dev/null 2>&1 || command -v 7z >/dev/null 2>&1; then
  ok "7z/unrar/unar present"
else
  miss "install unrar (or p7zip-rar) to open .cbr files; .cbz needs only 7-Zip"
fi

if command -v kindlegen >/dev/null 2>&1; then
  echo "== kindlegen self-test =="
  # Capture rather than pipe into grep -q: an early pipe close would fail a healthy binary under pipefail.
  KG_OUT="$(kindlegen 2>&1 || true)"
  if [[ "$KG_OUT" == *"Amazon kindlegen"* ]]; then ok "runs"; else miss "kindlegen does not run (Rosetta? quarantine?)"; fi
fi

echo
if [ "$MISSING" = 0 ]; then
  echo "All set."
else
  echo "Some pieces are missing; MOBI output may be unavailable. EPUB (Send to Kindle) and KEPUB (Kobo) still work."
  exit 2
fi
