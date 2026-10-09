#!/usr/bin/env python3
"""Compare a source-of-truth directory with derived directories, file by file.

Prints a matrix (rows = files in the source, columns = derived dirs) with:
  =  identical   ~  differs   -  missing in derived
  ~= same JSON key structure, different values (only for files matched by --shape)
then, per derived dir, the files that exist only there ("extra").
Exit code 1 if any file differs, is missing, or is extra, so it can gate CI. Files that only
differ in values under --shape (parametrised config) do not count as drift.

Usage:
    drift_matrix.py SOURCE DERIVED [DERIVED ...] [--only GLOB ...] [--ignore GLOB ...] [--shape GLOB ...]
    drift_matrix.py --selftest

Run it once per bucket of the audit: --only on the must-match paths, --shape on parametrised
JSON config. Globs match the path relative to the directory root (and each path segment).

Directories are compared as they sit on disk: check out the same ref first if that matters.
Default ignores skip VCS metadata, dependency folders, build output and caches.
"""
import argparse
import fnmatch
import hashlib
import json
import os
import sys

DEFAULT_IGNORE = [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
                  ".next", ".cache", "*.pyc", ".DS_Store", "*.log"]


def ignored(rel, patterns):
    parts = rel.split(os.sep)
    return any(fnmatch.fnmatch(p, pat) or fnmatch.fnmatch(rel, pat) for pat in patterns for p in parts)


def list_files(root, patterns):
    found = set()
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not ignored(os.path.relpath(os.path.join(base, d), root), patterns)]
        for f in files:
            rel = os.path.relpath(os.path.join(base, f), root)
            if not ignored(rel, patterns):
                found.add(rel)
    return found


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def json_shape(node):
    """Key structure of a JSON document with values replaced by their type name."""
    if isinstance(node, dict):
        return {k: json_shape(v) for k, v in node.items()}
    return "list" if isinstance(node, list) else type(node).__name__


def status(src_path, dst_path, rel, shape):
    if not os.path.isfile(dst_path):
        return "-"
    if digest(src_path) == digest(dst_path):
        return "="
    if shape and any(fnmatch.fnmatch(rel, g) for g in shape):
        try:
            with open(src_path) as a, open(dst_path) as b:
                return "~=" if json_shape(json.load(a)) == json_shape(json.load(b)) else "~"
        except ValueError:
            pass
    return "~"


def compare(source, derived_dirs, ignore, only=None, shape=None):
    """Return (rows, extras): rows[path] = [status per derived], extras[dir] = sorted extra paths."""
    src_files = {f for f in list_files(source, ignore) if not only or any(fnmatch.fnmatch(f, o) for o in only)}
    rows = {}
    for rel in sorted(src_files):
        rows[rel] = [status(os.path.join(source, rel), os.path.join(d, rel), rel, shape) for d in derived_dirs]
    extras = {d: sorted(f for f in list_files(d, ignore) - src_files
                        if not only or any(fnmatch.fnmatch(f, o) for o in only)) for d in derived_dirs}
    return rows, extras


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="*")
    ap.add_argument("--ignore", nargs="*", default=[], help="extra glob patterns to skip")
    ap.add_argument("--only", nargs="*", help="restrict the comparison to these globs")
    ap.add_argument("--shape", nargs="*", help="JSON files compared by key structure, not values")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if len(args.dirs) < 2:
        ap.error("need SOURCE and at least one DERIVED directory")

    source, derived = args.dirs[0], args.dirs[1:]
    rows, extras = compare(source, derived, DEFAULT_IGNORE + args.ignore, args.only, args.shape)
    names = [os.path.basename(os.path.normpath(d)) for d in derived]
    print("legend: = identical   ~ differs   - missing in derived   ~= same keys, other values\n")
    print("| file | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    drifted = 0
    for rel, st in rows.items():
        if set(st) - {"=", "~="}:
            drifted += 1
        if set(st) != {"="}:
            print(f"| {rel} | " + " | ".join(st) + " |")
    print(f"\n{drifted} of {len(rows)} source files differ or are missing somewhere.")
    for d, name in zip(derived, names):
        if extras[d]:
            print(f"\nextra in {name} ({len(extras[d])}): " + ", ".join(extras[d][:30]) +
                  (" ..." if len(extras[d]) > 30 else ""))
    sys.exit(1 if drifted or any(extras.values()) else 0)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        def put(d, rel, text):
            p = os.path.join(t, d, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(text)
        for d in ("src", "a", "b"):
            put(d, "ci/build.yml", "same")
            put(d, "node_modules/x.js", "ignored")
        put("src", "run.sh", "v2")
        put("a", "run.sh", "v2")
        put("b", "run.sh", "v1")      # stale copy
        put("src", "only_src.txt", "x")  # missing everywhere
        put("src", "cfg.json", '{"name": "s", "retries": 3}')
        put("a", "cfg.json", '{"name": "a", "retries": 5}')  # parametrised: same keys, other values
        put("b", "cfg.json", '{"name": "b"}')                # shape drift: key missing
        put("b", "local.txt", "x")    # extra in b
        rows, extras = compare(os.path.join(t, "src"), [os.path.join(t, "a"), os.path.join(t, "b")], DEFAULT_IGNORE,
                               shape=["cfg.json"])
        assert rows["ci/build.yml"] == ["=", "="]
        assert rows["run.sh"] == ["=", "~"]
        assert rows["only_src.txt"] == ["-", "-"]
        assert rows["cfg.json"] == ["~=", "~"]
        assert "node_modules/x.js" not in rows
        assert extras[os.path.join(t, "b")] == ["local.txt"] and extras[os.path.join(t, "a")] == []
    print("selftest ok")


if __name__ == "__main__":
    main()
