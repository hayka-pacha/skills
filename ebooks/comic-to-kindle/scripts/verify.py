#!/usr/bin/env python3
"""comic-to-kindle: verify files produced by kcc-c2e before they go to the reader.

Usage:
  verify.py -p PROFILE [--manga] [--source INPUT] [--max-mb 200] [--keep] OUTPUT...

Checks, per file:
  EPUB / KEPUB / CBZ  every page fits the device screen (rotated spreads allowed),
                      no more near-blank pages than the source (publishers leave a few white
                      pages at the end of a volume; a broken build blanks most of them),
                      fixed-layout metadata present, reading direction right-to-left when
                      --manga, page count >= source (--source), size <= --max-mb
  MOBI                PalmDB "BOOKMOBI" signature, record count, non-trivial size

Exit status 1 when any check fails. Pages are extracted to a temp directory whose path is
printed, so two or three of them can be opened and eyeballed (the script checks geometry,
not whether the art looks right).

Blank-page detection needs Pillow. If it is not importable, the script re-executes itself
with the Python interpreter of the kcc-c2e installation, which always has Pillow.
"""
import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

# Device profiles as (width, height), mirrored from KCC's image.py.
PROFILES = {
    "K1": (600, 670), "K2": (600, 670), "KDX": (824, 1000), "K34": (600, 800), "K57": (600, 800),
    "KPW": (758, 1024), "KV": (1072, 1448), "KPW34": (1072, 1448), "K810": (600, 800),
    "KO": (1264, 1680), "K11": (1072, 1448), "KPW5": (1236, 1648), "KPW6": (1272, 1696),
    "KS1860": (1860, 1920), "KS1920": (1920, 1920), "KS1240": (1240, 1860), "KS1324": (1324, 1986),
    "KS": (1860, 2480), "KCS": (1272, 1696), "KS3": (1986, 2648), "KSCS": (1986, 2648),
    "KoMT": (600, 800), "KoG": (768, 1024), "KoGHD": (1072, 1448), "KoA": (758, 1024),
    "KoAHD": (1080, 1440), "KoAH2O": (1080, 1430), "KoAO": (1404, 1872), "KoN": (758, 1024),
    "KoC": (1072, 1448), "KoCC": (1072, 1448), "KoL": (1264, 1680), "KoLC": (1264, 1680),
    "KoF": (1440, 1920), "KoS": (1440, 1920), "KoE": (1404, 1872),
    "Rmk1": (1404, 1872), "Rmk2": (1404, 1872), "RmkPP": (1620, 2160), "RmkPPMove": (954, 1696),
}
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")
BLANK_MEAN = 250  # mean gray above this = page is (almost) entirely white


def ensure_pillow(argv):
    """Re-exec with kcc's interpreter when Pillow is missing here."""
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("C2K_REEXEC"):
        print("warning: Pillow unavailable, blank-page check skipped", file=sys.stderr)
        return
    kcc = shutil.which("kcc-c2e") or os.path.expanduser("~/.local/bin/kcc-c2e")
    if os.path.exists(kcc):
        py = os.path.join(os.path.dirname(os.path.realpath(kcc)), "python")
        if os.path.exists(py):
            os.environ["C2K_REEXEC"] = "1"
            os.execv(py, [py, os.path.abspath(__file__)] + argv)
    print("warning: Pillow unavailable, blank-page check skipped", file=sys.stderr)


def image_size(data):
    """(w, h) from PNG or JPEG bytes without Pillow."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
    return None


def mean_gray(path):
    try:
        from PIL import Image, ImageStat
    except ImportError:
        return None
    with Image.open(path) as im:
        return ImageStat.Stat(im.convert("L")).mean[0]


def count_source_pages(src):
    """Image entries in the source archive; None if it cannot be listed."""
    if os.path.isdir(src):
        return sum(1 for r, _, fs in os.walk(src) for f in fs if f.lower().endswith(IMG_EXT))
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            return sum(1 for n in z.namelist() if n.lower().endswith(IMG_EXT))
    for cmd in (["tar", "-tf", src], ["7z", "l", "-ba", src], ["7zz", "l", "-ba", src], ["unrar", "lb", src]):
        if shutil.which(cmd[0]):
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                return sum(1 for line in r.stdout.splitlines() if line.strip().lower().endswith(IMG_EXT))
    return None


def count_source_blank(src):
    """Near-blank images in the source archive or folder; None if it cannot be extracted or Pillow is missing."""
    try:
        from PIL import Image, ImageStat  # noqa: F401
    except ImportError:
        return None
    tmp = None
    root = src
    if not os.path.isdir(src):
        tmp = tempfile.mkdtemp(prefix="c2k-src-")
        if zipfile.is_zipfile(src):
            with zipfile.ZipFile(src) as z:
                z.extractall(tmp)
        elif shutil.which("tar") and subprocess.run(["tar", "-xf", src, "-C", tmp], capture_output=True).returncode == 0:
            pass
        elif shutil.which("7z") and subprocess.run(["7z", "x", "-y", f"-o{tmp}", src], capture_output=True).returncode == 0:
            pass
        else:
            shutil.rmtree(tmp, ignore_errors=True)
            return None
        root = tmp
    n = 0
    for r, _, fs in os.walk(root):
        for f in fs:
            if f.lower().endswith(IMG_EXT):
                m = mean_gray(os.path.join(r, f))
                if m is not None and m > BLANK_MEAN:
                    n += 1
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return n


def check_zip(path, width, height, manga, max_mb, source_pages, keep, source_blank=None):
    fails, notes = [], []
    size_mb = os.path.getsize(path) / 1e6
    tmp = tempfile.mkdtemp(prefix="c2k-verify-")
    with zipfile.ZipFile(path) as z:
        z.extractall(tmp)
    images = sorted(
        os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.lower().endswith(IMG_EXT)
    )
    pages = [p for p in images if "cover" not in os.path.basename(p).lower()] or images
    notes.append(f"pages={len(pages)} size={size_mb:.0f}MB")

    too_big, blank, unreadable = [], [], []
    for p in images:
        with open(p, "rb") as fh:
            dims = image_size(fh.read())
        if dims is None:
            unreadable.append(os.path.basename(p))
            continue
        w, h = dims
        if not ((w <= width and h <= height) or (w <= height and h <= width)):
            too_big.append(f"{os.path.basename(p)} {w}x{h}")
        m = mean_gray(p)
        if m is not None and m > BLANK_MEAN:
            blank.append(f"{os.path.basename(p)} mean={m:.0f}")
    if too_big:
        fails.append(f"{len(too_big)} page(s) exceed {width}x{height}: {too_big[:3]}")
    if blank:
        # Publishers leave a few white pages at the end of a volume; those are not a defect.
        # A broken conversion blanks most pages. So: fail when the output has more blank pages
        # than the source, or when more than 10% of pages are blank and no source was given.
        if source_blank is not None:
            if len(blank) > source_blank:
                fails.append(f"{len(blank)} near-blank page(s) but only {source_blank} in the source: {blank[:5]}")
            else:
                notes.append(f"blank={len(blank)} (same in source)")
        elif len(blank) > max(1, len(pages) // 10):
            fails.append(f"{len(blank)} near-blank page(s), {100 * len(blank) // max(1, len(pages))}% of the book: {blank[:5]}")
        else:
            notes.append(f"blank={len(blank)} (pass --source to confirm they are the publisher's)")
    if unreadable:
        fails.append(f"{len(unreadable)} unreadable image(s): {unreadable[:3]}")
    if not images:
        fails.append("no page images inside the archive")

    opfs = [os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs if f.endswith(".opf")]
    if opfs:
        with open(opfs[0], encoding="utf-8", errors="ignore") as fh:
            opf = fh.read()
        fixed = 'name="fixed-layout" content="true"' in opf or "rendition:layout" in opf and "pre-paginated" in opf
        if not fixed:
            fails.append("no fixed-layout metadata (reader will add margins / reflow)")
        rtl = 'content="horizontal-rl"' in opf or 'page-progression-direction="rtl"' in opf
        if manga and not rtl:
            fails.append("reading direction is not right-to-left (missing -m?)")
        notes.append("direction=" + ("rtl" if rtl else "ltr"))
        m = re.search(r'name="original-resolution" content="(\d+)x(\d+)"', opf)
        if m and (int(m.group(1)), int(m.group(2))) != (width, height):
            fails.append(f"built for {m.group(1)}x{m.group(2)}, expected {width}x{height} (wrong profile?)")
    elif path.lower().endswith(".epub"):
        fails.append("no OPF found inside EPUB")

    if source_pages is not None and len(pages) < source_pages:
        fails.append(f"page count dropped: {len(pages)} < {source_pages} in source")
    if max_mb and size_mb > max_mb:
        fails.append(f"{size_mb:.0f} MB exceeds {max_mb} MB (Send to Kindle rejects it; use --ts)")
    if path.lower().endswith(".kepub.epub"):
        notes.append("kepub (Kobo native)")

    if keep:
        notes.append(f"extracted to {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return fails, notes


def check_mobi(path):
    fails, notes = [], []
    size_mb = os.path.getsize(path) / 1e6
    with open(path, "rb") as fh:
        head = fh.read(4096)
    if head[60:68] != b"BOOKMOBI":
        fails.append("not a MOBI (missing BOOKMOBI signature)")
    else:
        records = struct.unpack(">H", head[76:78])[0]
        notes.append(f"records={records} size={size_mb:.0f}MB")
        if records < 10:
            fails.append("suspiciously few records; kindlegen may have failed mid-way")
    if size_mb < 1:
        fails.append("file under 1 MB; conversion almost certainly failed")
    notes.append("copy to the Kindle's documents/ folder over USB; Send to Kindle no longer accepts MOBI")
    return fails, notes


def main():
    ensure_pillow(sys.argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-p", "--profile", required=True, choices=sorted(PROFILES), metavar="PROFILE")
    ap.add_argument("--manga", action="store_true", help="expect right-to-left reading direction")
    ap.add_argument("--source", help="original archive or folder, to compare page counts")
    ap.add_argument("--max-mb", type=float, default=200, help="EPUB size limit (Send to Kindle: 200). 0 disables")
    ap.add_argument("--keep", action="store_true", help="keep extracted pages for eyeballing")
    ap.add_argument("outputs", nargs="+")
    a = ap.parse_args()

    width, height = PROFILES[a.profile]
    source_pages = count_source_pages(a.source) if a.source else None
    source_blank = count_source_blank(a.source) if a.source else None
    if a.source and source_pages is None:
        print(f"note: could not count pages in {a.source}")

    any_fail = False
    for out in a.outputs:
        if not os.path.isfile(out):
            print(f"FAIL {out}: missing")
            any_fail = True
            continue
        low = out.lower()
        if low.endswith(".mobi") or low.endswith(".azw3"):
            fails, notes = check_mobi(out)
        elif zipfile.is_zipfile(out):
            fails, notes = check_zip(out, width, height, a.manga, a.max_mb, source_pages, a.keep, source_blank)
        else:
            fails, notes = ["unknown format (expected .epub/.kepub.epub/.cbz/.mobi)"], []
        status = "FAIL" if fails else "OK  "
        any_fail = any_fail or bool(fails)
        print(f"{status} {os.path.basename(out)}  " + "  ".join(notes))
        for f in fails:
            print(f"     - {f}")
    if source_pages is not None:
        print(f"source pages: {source_pages}")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
