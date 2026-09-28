# Troubleshooting

Symptom first, then the cause and the fix. Most of these come from skipping KCC or from a wrong profile, not from the reader.

## On the device

| Symptom | Cause | Fix |
|---|---|---|
| Pages are blank / white | EPUB assembled by hand: images referenced with wrong paths, or too large for the reader to decode | Rebuild with `convert.sh`. Run `verify.py`; it flags near-blank pages. |
| Pages are cut, need panning, or show a zoomed corner | Images larger than the screen with no fixed-layout metadata; or a profile for a bigger device | Check the profile in `references/device-profiles.md`. Never use `-n` (no processing) for a reader. |
| Big white margins, small page in the middle | No fixed-layout metadata, or a profile for a smaller device | Right profile; KCC sets `zero-margin` and `fixed-layout` itself. |
| Manga reads in the wrong order | Missing `-m` | Re-run with `-m`. Direction is baked into the file; it cannot be changed on the device. |
| Left-to-right comic reads backwards | `-m` was used on a Western comic | Re-run without `-m`. |
| Double-page spreads split badly, or halves in the wrong order | Splitter mode | `-- -r 1` rotates spreads instead of splitting; `-- -r 2` provides both; `--spreadshift` when spreads are misaligned by one page. |
| Page numbers or gutters cropped too aggressively | Cropping level 2 (margins + page numbers) is the default | `-- -c 1` keeps page numbers, `-- -c 0` disables cropping. |
| Too dark or washed out | Gamma auto-detection missed | `-- -g 1.0` for neutral, `-- --autolevel` to force black point, `-- --noautocontrast` to leave scans alone. |
| Colour pages came out gray | KCC grayscales by default | `-- --forcecolor` (only useful on colour devices). |
| Cover missing or wrong title in the library | Metadata taken from the file name | `-a "Author"`, `--lang`, and `-- -t "Title"`; `-- --metadatatitle 2` uses ComicInfo.xml. |
| Landscape mode shows one page stretched | Panel view defaults | `-- --onepagelandscape`. |

## Transfer

| Symptom | Cause | Fix |
|---|---|---|
| Send to Kindle refuses the file | Over 200 MB, or a MOBI (Amazon stopped accepting MOBI/AZW in 2022) | Send the `.epub`; add `-- --ts 190` so KCC keeps each volume under the limit, or `-- -b 1` to split long volumes. |
| Kindle over USB does not list the file | An `.epub` was copied; Kindles do not open EPUB from the file system | Copy the `.mobi` into `documents/`. If no `.mobi` exists, kindlegen was missing: run `setup.sh` and re-convert with `-f MOBI+EPUB`. |
| Kobo shows the file but pages look like a regular EPUB with margins | `.epub` instead of `.kepub.epub`, or the file was renamed | Keep the `.kepub.epub` name KCC produces. |

## Tooling

| Message | Cause | Fix |
|---|---|---|
| `kcc-c2e: command not found` | `~/.local/bin` not on PATH, or not installed | `scripts/setup.sh`; the scripts prepend `~/.local/bin` themselves. |
| `ERROR: KindleGen is missing!` | No `kindlegen` on PATH | `scripts/setup.sh` extracts it from Kindle Previewer on macOS. Linux: no kindlegen exists; use `-f EPUB` and Send to Kindle. |
| `kindlegen: Bad CPU type in executable` | Apple Silicon without Rosetta | `softwareupdate --install-rosetta --agree-to-license`. |
| `kindlegen` killed or "cannot be opened" on macOS | Gatekeeper quarantine on the extracted binary | `xattr -c ~/.local/bin/kindlegen`. |
| CBR fails to open / zero pages | No RAR-capable tool | macOS `tar` reads RAR; elsewhere install `p7zip` or `unrar`. |
| `No solution found ... kindlecomicconverter was not found` | Tried to install from PyPI | Install from GitHub: `uv tool install "git+https://github.com/ciromattia/kcc.git"`. |
| PDF input renders blurry | Vector PDF rasterised at the wrong size | `-- --pdfwidth` renders to device width instead of height. |
| Conversion is slow | Normal: about a minute per 200 pages; KCC already uses every core | Run volumes one after another, not in parallel. |
| Output has fewer pages than the source, or a truncated EPUB, although KCC reported success | Another `kcc-c2e` started meanwhile: on startup it deletes every `KCC-*` folder in the shared temp directory | Never run two bare `kcc-c2e` at once. `convert.sh` isolates `TMPDIR` per run; re-run the volume with it. `verify.py --source` catches the page loss. |
| `ERROR: 7z is missing!` | KCC checks for `7zz` (macOS) or `7z` (elsewhere) before opening any CBZ/CBR, whatever tool extracts it | macOS `brew install sevenzip`; Debian/Ubuntu `apt install p7zip-full`; then make sure it is on PATH. |
| `Extraction failed` on a `.cbr` | No RAR-capable extractor, or the temp directory is not writable | On macOS `tar` handles RAR; check `TMPDIR` is writable. On Linux install `unrar` or `p7zip-rar`. |

## Before asking the user to re-test on the device

Run `verify.py` with `--keep` and look at three extracted pages. A file that passes the geometry checks and looks right on three pages has, in practice, always rendered correctly on the reader. A file that was not verified is the one that comes back an hour later with "it is cut again".
