#!/usr/bin/env python3
"""Inventory documentation files and flag where docs and code disagree. Read-only.

    python3 <skill-folder>/scripts/check_docs.py [REPO_ROOT] [--readme README.md] [--specs docs/PRODUCT-SPECS.md]
    python3 <skill-folder>/scripts/check_docs.py --selftest

Inventory (Markdown files plus bare LICENSE/COPYING/NOTICE files):
  keep        the one README and the one specs file (the target layout)
  protected   files tools or conventions need (CLAUDE.md and its @imports, SKILL.md folders,
              LICENSE/CHANGELOG/CONTRIBUTING/SECURITY/..., .github/, .claude/): never merge or delete
  candidate   every other .md: merge its useful content into a keeper, then propose deletion
Checks, across all .md files:
  - shadowing READMEs (GitHub shows .github/ first, then root, then docs/)
  - broken relative links, and .md files mentioned anywhere in the text that do not exist
  - backticked path-like tokens that match no file (heuristic; lockfiles and build folders skipped)
  - `npm|pnpm|yarn run X` not in package.json scripts, `make X` not a Makefile target (repo root only)
  - env vars named in docs but absent from the code, and env vars read in code but never documented
  - keepers or protected files that still point at a candidate (fix before deleting it)
Exit code 1 if anything is flagged or candidates remain.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "dist", "build", "__pycache__", ".next", "vendor"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock", "go.sum",
             "composer.lock", "Gemfile.lock", "uv.lock"}
PROTECTED_NAMES = {"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "SKILL.md", "LICENSE.md", "CHANGELOG.md",
                   "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md", "SUPPORT.md", "ACCESSIBILITY.md"}
BARE_PROTECTED = ("LICENSE", "COPYING", "NOTICE")
PATH_TOKEN = re.compile(r"^[\w.\-]+(/[\w.\-]+)+/?$|^[\w\-]+\.(py|js|ts|sh|json|ya?ml|toml|md|sql|html|css|env)$")
MD_MENTION = re.compile(r"(?<![\w/.\-:])((?:[\w.\-]+/)*[\w.\-]+\.md)\b")
ENV_TOKEN = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")  # SNAKE_CASE, always an env candidate
CAPS_WORD = re.compile(r"^[A-Z][A-Z0-9]{2,}$")             # PORT, HOST: only when the line talks about env/config
ENV_CONTEXT = re.compile(r"env|variable|config", re.I)
ENV_READ = re.compile(r"(?:process\.env\.|process\.env\[[\"']|os\.environ(?:\.get)?[(\[]\s*[\"']"
                      r"|getenv\(\s*[\"']|env::var\(\s*\")([A-Z][A-Z0-9_]+)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
TICK = re.compile(r"`([^`\n]+)`")
RUN_CMD = re.compile(r"^(?:npm|pnpm|yarn) run ([\w:.\-]+)")
MAKE_CMD = re.compile(r"^make ([\w.\-]+)")


def walk(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            yield os.path.relpath(os.path.join(base, f), root)


def read(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        return ""


def has_word(text, word):
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(word)}(?![A-Za-z0-9_])", text) is not None


def classify(root, files, readme, specs):
    docs = [f for f in files if f.endswith(".md") or os.path.basename(f).upper().startswith(BARE_PROTECTED)]
    skill_dirs = {os.path.dirname(f) for f in docs if os.path.basename(f) == "SKILL.md"}
    imported = set()
    for f in docs:
        if os.path.basename(f).startswith("CLAUDE"):
            for m in re.findall(r"(?<![\w`])@([\w./\-]+\.md)", read(root, f)):
                imported.add(os.path.normpath(os.path.join(os.path.dirname(f), m)))
    out = {"keep": [], "protected": [], "candidate": []}
    for f in docs:
        top = f.split(os.sep)[0]
        if f in (readme, specs):
            out["keep"].append(f)
        elif (os.path.basename(f) in PROTECTED_NAMES or os.path.basename(f).upper().startswith(BARE_PROTECTED)
              or top in (".github", ".claude") or f in imported
              or any(f == d or f.startswith(d + os.sep) for d in skill_dirs if d)):
            out["protected"].append(f)
        else:
            out["candidate"].append(f)
    return out


def project_commands(root):
    scripts, targets = None, None
    try:
        scripts = set(json.loads(read(root, "package.json") or "null")["scripts"])
    except (TypeError, KeyError, ValueError):
        pass
    makefile = read(root, "Makefile")
    if makefile:
        targets = set(re.findall(r"^([\w.\-/]+)\s*:(?!=)", makefile, re.M))
    return scripts, targets


def check(root, readme="README.md", specs=os.path.join("docs", "PRODUCT-SPECS.md")):
    files = sorted(walk(root))
    fileset, basenames = set(files), {os.path.basename(f) for f in files}
    mds = [f for f in files if f.endswith(".md")]
    classes = classify(root, files, readme, specs)
    found = {"classes": classes, "shadow": [], "links": [], "paths": set(), "commands": [], "pointers": [],
             "env_docs_only": set(), "env_code_only": set()}

    readmes = [f for f in (os.path.join(".github", "README.md"), "README.md", os.path.join("docs", "README.md"))
               if f in fileset]
    found["shadow"] = readmes if len(readmes) > 1 else []

    def exists(tok, here):
        p = os.path.normpath(tok.rstrip("/"))
        return (p in fileset or os.path.normpath(os.path.join(here, p)) in fileset
                or os.path.isdir(os.path.join(root, p)) or os.path.basename(p) in basenames)

    scripts, targets = project_commands(root)
    documented_env, doc_text = set(), ""
    for md in mds:
        text = read(root, md)
        doc_text += text
        here = os.path.dirname(md)
        for target in LINK.findall(text):
            t = target.split("#")[0]
            if t and not re.match(r"^[a-z]+:", t) and not t.startswith("/"):
                if os.path.normpath(os.path.join(here, t)) not in fileset and not os.path.isdir(os.path.join(root, here, t)):
                    found["links"].append(f"{md}: {target}")
        for m in MD_MENTION.findall(LINK.sub("", text)):  # links are reported separately above
            if not exists(m, here):
                found["paths"].add(f"{md}: `{m}`")
        for line in text.splitlines():
            for tok in TICK.findall(line):
                name = tok.split("=")[0]
                if ENV_TOKEN.match(name) or (CAPS_WORD.match(name) and ENV_CONTEXT.search(line)):
                    documented_env.add(name)
                    continue
                run, make = RUN_CMD.match(tok), MAKE_CMD.match(tok)
                if run and scripts is not None and run.group(1) not in scripts:
                    found["commands"].append(f"{md}: `{tok}` (no such script in package.json)")
                elif make and targets is not None and make.group(1) not in targets:
                    found["commands"].append(f"{md}: `{tok}` (no such Makefile target)")
                elif (PATH_TOKEN.match(tok) and not tok.startswith(("http", "/", "~", "-"))
                      and tok.split("/")[0] not in SKIP_DIRS and os.path.basename(tok) not in LOCKFILES
                      and not exists(tok, here)):
                    found["paths"].add(f"{md}: `{tok}`")

    code_text, read_env = "", set()
    for f in files:
        if not f.endswith(".md") and os.path.getsize(os.path.join(root, f)) < 1_000_000:
            text = read(root, f)
            code_text += text
            read_env.update(ENV_READ.findall(text))
    found["env_docs_only"] = {v for v in documented_env if not has_word(code_text, v)}
    found["env_code_only"] = {v for v in read_env if not has_word(doc_text, v)}

    for f in classes["keep"] + classes["protected"]:
        text = read(root, f)
        for c in classes["candidate"]:
            if c.replace(os.sep, "/") in text or has_word(text, os.path.basename(c)):
                found["pointers"].append(f"{f} -> {c}")
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--specs", default=os.path.join("docs", "PRODUCT-SPECS.md"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    r = check(args.root, args.readme, args.specs)
    for name in ("keep", "protected", "candidate"):
        print(f"\n== {name} ({len(r['classes'][name])}) ==")
        for f in r["classes"][name]:
            print(f"  {f}")
    flagged = 0
    for title, key in (("README files that shadow each other", "shadow"), ("Broken relative links", "links"),
                       ("Documented paths that match no file", "paths"),
                       ("Documented commands that do not exist", "commands"),
                       ("Env vars documented but not in code (stale?)", "env_docs_only"),
                       ("Env vars read in code but never documented", "env_code_only"),
                       ("Keepers/protected files pointing at a candidate (fix before deleting it)", "pointers")):
        items = sorted(r[key])
        if items:
            flagged += len(items)
            print(f"\n== {title} ({len(items)}) ==")
            for i in items:
                print(f"  {i}")
    if not r["classes"]["keep"]:
        print("\nnote: neither the README nor the specs file exists yet")
    sys.exit(1 if flagged or r["classes"]["candidate"] else 0)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        def put(rel, text=""):
            p = os.path.join(t, rel)
            os.makedirs(os.path.dirname(p) or t, exist_ok=True)
            with open(p, "w") as f:
                f.write(text)
        put("README.md", "Run `src/app.py`, `npm run serve` and `npm run start`; `scripts/gone.sh` is old. See `package-lock.json`.\n"
                         "Env: `API_TOKEN`, `HTTP_PORT`. The environment variable `HOST` sets the bind address.\n"
                         "Docs: [x](docs/missing.md), docs/ghost.md\n")
        put("package.json", json.dumps({"scripts": {"start": "node src/app.py"}}))
        put("docs/PRODUCT-SPECS.md", "specs")
        put("docs/notes.md", "scratch")
        put("CLAUDE.md", "@docs/guide.md\nSee docs/notes.md for details.\n")
        put("docs/guide.md", "imported by CLAUDE.md")
        put("LICENSE", "MIT")
        put("skills/s/SKILL.md", "x")
        put("skills/s/references/r.md", "x")
        put(".github/README.md", "shadow")
        put("src/app.py", "import os\nos.environ['API_TOKEN']\nos.environ['PORT']\nos.getenv('NEW_SETTING')\n")
        r = check(t)
        c = r["classes"]
        j = os.path.join
        assert sorted(c["keep"]) == ["README.md", j("docs", "PRODUCT-SPECS.md")]
        assert {"LICENSE", j("docs", "guide.md"), j("skills", "s", "references", "r.md")} <= set(c["protected"])
        assert c["candidate"] == [j("docs", "notes.md")]
        assert r["shadow"] == [j(".github", "README.md"), "README.md"]
        assert r["links"] == ["README.md: docs/missing.md"]
        assert r["paths"] == {"README.md: `scripts/gone.sh`", "README.md: `docs/ghost.md`"}, r["paths"]
        assert r["commands"] == ["README.md: `npm run serve` (no such script in package.json)"], r["commands"]
        assert r["env_docs_only"] == {"HTTP_PORT", "HOST"}, r["env_docs_only"]
        assert r["env_code_only"] == {"PORT", "NEW_SETTING"}, r["env_code_only"]
        assert r["pointers"] == [f"CLAUDE.md -> {j('docs', 'notes.md')}"], r["pointers"]
    print("selftest ok")


if __name__ == "__main__":
    main()
