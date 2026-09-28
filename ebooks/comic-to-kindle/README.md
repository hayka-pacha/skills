# Comic to Kindle

Claude Code skill that converts comics and manga (CBZ, CBR, PDF, image folders) into files that display page-for-page on a Kindle, Kobo or reMarkable, using [Kindle Comic Converter](https://github.com/ciromattia/kcc) with the right device profile, and verifies the output before it reaches the reader.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/ebooks/comic-to-kindle" ~/.claude/skills/comic-to-kindle
```

Then, once, let the skill install its tools (or run it yourself):

```bash
~/.claude/skills/comic-to-kindle/scripts/setup.sh
```

## What it does

1. Maps the user's device ("Oasis 10th gen", "Paperwhite 2021", "Kobo Clara") to a KCC profile.
2. Installs what is missing: `kcc-c2e` from GitHub, `kindlegen` extracted from Kindle Previewer without sudo (macOS), a RAR reader for `.cbr`.
3. Picks the output format from the transfer method: `MOBI` for USB, `EPUB` for Send to Kindle, `.kepub.epub` for Kobo.
4. Converts one volume or a whole directory (resumable, sequential).
5. Verifies every output: page size within the screen, no blank pages, right-to-left flag for manga, page count against the source, Send to Kindle size limit, MOBI header.
6. Tells the user which file goes where, and asks for a device check on the first volume before doing a series.

## Structure

```
comic-to-kindle/
├── SKILL.md                      # Workflow: profile → tools → format → convert → verify → deliver
├── scripts/
│   ├── setup.sh                  # install/check kcc-c2e, kindlegen, RAR support
│   ├── convert.sh                # kcc-c2e wrapper: sane defaults, directories, resume
│   └── verify.py                 # geometry/metadata checks on EPUB, KEPUB, CBZ, MOBI
├── references/
│   ├── device-profiles.md        # marketing name / generation → KCC profile code
│   └── troubleshooting.md        # symptom → cause → flag
└── evals/
    └── evals.json                # skill quality evals
```

## Requirements

- Python 3.9+ and `uv` (or `pipx`) to install `kcc-c2e`.
- 7-Zip on PATH (`7zz` on macOS via `brew install sevenzip`, `7z` from `p7zip-full` on Linux): `kcc-c2e` checks for it before opening any archive.
- macOS: Homebrew, to fetch Kindle Previewer for `kindlegen` (only needed for MOBI). Apple Silicon needs Rosetta.
- Linux: MOBI is not buildable (Amazon ships kindlegen only for macOS/Windows); use EPUB + Send to Kindle.
- Windows: install Kindle Previewer; `kcc-c2e` finds `kindlegen` on its own.

Everything runs locally. Nothing is uploaded anywhere.

## Triggers

The skill auto-triggers on: converting CBZ/CBR/PDF comics or manga for a Kindle, Kobo, reMarkable or other e-ink reader; MOBI/AZW3/KEPUB from images; pages cut, blank, tiny, zoomed or in the wrong direction on a reader; how to send a comic to a Kindle (USB or Send to Kindle).
