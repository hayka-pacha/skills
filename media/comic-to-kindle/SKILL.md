---
name: comic-to-kindle
description: Convert comic and manga archives (CBZ, CBR, PDF, image folders) into files that display correctly on a Kindle, Kobo or reMarkable e-reader, using Kindle Comic Converter (kcc-c2e) with the right device profile, then verify the result before handing it over. Use this skill whenever the user wants to read a comic, manga, BD, webtoon or scanned book on an e-ink reader, mentions .cbz/.cbr files together with a Kindle or Kobo, asks for MOBI/AZW3/KEPUB made from images, complains that pages come out cut, blank, tiny, zoomed, with big margins or in the wrong reading direction on their reader, or asks how to get a comic onto their Kindle (USB or Send to Kindle). Do not use it for reflowable text EPUBs (use calibre) or for reading on a phone/tablet app.
metadata:
  version: 1.0.0
  platforms: [macos, linux, windows]
  hermes:
    tags: [kindle, kobo, manga, comics, cbz, cbr, mobi, kepub, ebook, e-reader, kcc]
    related_skills: []
---

# Comic to Kindle

Turn CBZ/CBR/PDF comics into e-reader files that render page-for-page on the target screen, with Kindle Comic Converter (KCC) and a verification pass.

## Why this skill exists

Hand-built EPUBs made from comic images fail on e-readers in predictable ways: pages show up blank (the reader refuses the image container or size), pages are cut or need panning (images were never resized to the screen), margins eat a third of the page (no fixed-layout metadata), and manga reads backwards (no right-to-left flag). Users then spend an evening re-sending files to the device.

KCC solves all of these at once: it resizes every page to the exact device resolution, writes fixed-layout metadata the reader understands, splits double-page spreads, sets reading direction, and calls kindlegen when a MOBI is needed. So the rule is simple: never assemble an EPUB by hand for a comic. Run KCC with the right profile, then check the output before declaring victory.

## Workflow

### 1. Identify the device and pick the profile

The profile decides the output resolution, so a wrong profile reproduces the "cut pages" problem. Common mappings:

| User says | Profile | Screen |
|-----------|---------|--------|
| Kindle Oasis 2 or 3 (9th/10th gen, 2017/2019) | `KO` | 1264x1680 |
| Kindle Paperwhite 5 / Signature (11th gen, 2021) | `KPW5` | 1236x1648 |
| Kindle Paperwhite 6 / Signature (12th gen, 2024) | `KPW6` | 1272x1696 |
| Kindle Paperwhite 3/4, Oasis 1, Voyage | `KPW34` | 1072x1448 |
| Kindle basic 2022/2024 (11th gen) | `K11` | 1072x1448 |
| Kindle Scribe | `KS` | 1860x2480 |
| Kindle Colorsoft | `KCS` | 1272x1696 |
| Kobo Clara HD / 2E / BW | `KoC` | 1072x1448 |
| Kobo Libra 2 / H2O | `KoL` | 1264x1680 |
| Kobo Libra Colour / Clara Colour | `KoLC` / `KoCC` | 1264x1680 / 1072x1448 |

The full table, including older models and reMarkable, is in `references/device-profiles.md`. If the user names a device that is not listed, match it by screen resolution or use `OTHER` with `--customwidth/--customheight`. If the device is unknown, ask once; guessing costs the user a full re-transfer.

### 2. Check the tooling

```bash
scripts/setup.sh --check     # reports what is present
scripts/setup.sh             # installs what is missing
```

What it installs and why:

- `kcc-c2e`, the KCC command line. It is not on PyPI under a stable name, so it is installed from the GitHub repository with `uv tool` (or pipx).
- `kindlegen`, required only for MOBI output. Amazon ships it inside Kindle Previewer. On macOS the script fetches the Previewer package with Homebrew and unpacks the binary without sudo. On Apple Silicon it needs Rosetta. On Linux there is no kindlegen: produce EPUB and deliver through Send to Kindle.
- 7-Zip (`7zz` on macOS, `7z` elsewhere): `kcc-c2e` refuses any CBZ/CBR input when it is absent, even though macOS `tar` does the actual RAR extraction. On Linux `.cbr` additionally needs `unrar` or `p7zip-rar`.

Read the check output and adapt the format in the next step instead of retrying a failing MOBI build.

### 3. Choose the output format from how the file reaches the device

| Device | Transfer | Format | Notes |
|--------|----------|--------|-------|
| Kindle | USB cable | `MOBI` | Copy into the Kindle's `documents/` folder. Needs kindlegen. |
| Kindle | Send to Kindle (app, web, email) | `EPUB` | Amazon converts it server side. 200 MB limit per file; MOBI is no longer accepted this way. |
| Kindle | Not sure | `MOBI+EPUB` | Both files in one run. This is the default for Kindle profiles when kindlegen is present. |
| Kobo | USB cable | `EPUB` | KCC writes `.kepub.epub`, which Kobo renders with its fast native engine. Drop it anywhere on the device. |
| reMarkable | App or USB web UI | `PDF` | |

For Send to Kindle, add `-- --ts 190` so KCC keeps each file under the limit.

### 4. Convert

```bash
scripts/convert.sh -p KO -m -o ~/Comics/Series/converted ~/Comics/Series/Vol01.cbz
```

- `-p` profile from step 1.
- `-m` for manga read right to left. Japanese manga keep their original direction in almost every French and English edition, so use it unless the user says otherwise. Western comics, BD and webtoons read left to right: leave it out.
- `-o` output directory. Defaults to a `converted/` folder next to the input.
- `-a "Author"` and `--lang fr-FR` when known: the reader shows them in the library.
- Directories as input convert every archive inside, sorted. Existing outputs are skipped, so an interrupted batch can be re-run.
- Anything after `--` goes straight to `kcc-c2e` (see `kcc-c2e --help`): `-r 1` rotates spreads instead of splitting, `--ts 190` caps file size, `-c 0` disables margin cropping if the user wants raw pages.

Expect roughly one minute per 200-page volume. Run volumes sequentially, in one `convert.sh` call: KCC already uses all cores, and worse, every `kcc-c2e` start deletes all KCC working folders in the shared temp directory, so two conversions running at once silently lose pages. `convert.sh` gives each of its runs a private temp directory; a bare `kcc-c2e` launched in parallel does not get that protection.

### 5. Verify before handing over

```bash
scripts/verify.py -p KO --manga --source ~/Comics/Series/Vol01.cbz ~/Comics/Series/converted/Vol01.*
```

The script fails loudly when a page exceeds the device resolution, a page is near-blank, the reading direction is missing, the page count dropped below the source, an EPUB is over the Send to Kindle limit, or a MOBI has a broken header. Those are exactly the failures users report after the fact, so do not skip this step even for one file.

The script checks geometry, not content. Also open two or three extracted pages (cover, an early page, a page from the middle) and look at them: text legible, panels intact, nothing rotated by mistake. The extraction directory is printed by the script.

### 6. Deliver

Tell the user, in this order:

1. Where the files are and which one to use for their transfer method (USB gets the `.mobi`, Send to Kindle gets the `.epub`, Kobo gets the `.kepub.epub`).
2. What was verified (page count, resolution, direction, blank pages) and what was not: rendering on the physical device. Ask them to check the first volume on the reader before converting a whole series.
3. For a series: convert one volume, wait for that confirmation, then run the rest with the same command on the directory.

## Quick reference

```bash
scripts/setup.sh --check
scripts/convert.sh -p <PROFILE> [-m] [-a "Author"] [--lang xx-XX] -o <outdir> <files or dirs> [-- extra kcc flags]
scripts/verify.py -p <PROFILE> [--manga] [--source <input>] <outputs>
```

## When something looks wrong

Read `references/troubleshooting.md`. It maps each symptom (blank pages, cut pages, wrong direction, spreads split badly, file rejected by Send to Kindle, "KindleGen is missing", CBR fails to open) to its cause and the flag that fixes it.
