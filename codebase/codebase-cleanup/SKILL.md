---
name: codebase-cleanup
description: >-
  Scan a whole codebase for incoherences and clean it up safely: debug files, temporary files,
  orphaned or never-used files, dead or obsolete code, unused dependencies, one-shot scripts that
  were run once and never again, duplication, outdated dependency versions, and a CLAUDE.md and
  .gitignore that no longer match reality. Every deletion is proposed and confirmed first. Use
  this skill whenever the user asks to clean up, tidy, prune, declutter, de-bloat or audit a
  repo, find dead code or unused files, update dependencies, apply KISS and DRY, or says the
  codebase "feels messy", even if they never name a specific kind of clutter.
metadata:
  version: 1.0.0
---

# Codebase Cleanup

Cleanup is deletion, and deletion is the one edit you cannot always see the consequences of.
So the rule is: detect broadly, verify each candidate, show the evidence, and let the user decide
before anything is removed. Git history is the safety net; it only works if the work is
committed in small, separate steps.

## Workflow

### 0. Baseline
Check `git status` is clean (or note what is dirty and leave it alone). Work on a branch. Run the
project's build and tests now and record the result. "Still green" at the end is only meaningful
against a known-green start. If the baseline is red, say so and clean around it.

### 1. Inventory candidates
Collect, do not delete. Categories, with how to find each (commands per ecosystem in
`references/detectors.md`):

| Category | Signals |
|---|---|
| **Debug leftovers** | Debug dumps, screenshots, scratch notebooks, `*.orig`/`*.bak`, committed logs, stray `print`/`console.log`/`debugger` |
| **Temporary files** | `tmp`, `scratch`, editor swap files, generated output committed by accident |
| **Orphaned files** | Nothing references the file by name and it is not an entry point |
| **Dead / obsolete code** | Detector findings: unused exports, unreachable branches, flags that can no longer vary |
| **Unused dependencies** | Declared but never imported; or imported but undeclared |
| **One-shot files** | Migration, backfill, fix or import scripts run once. Signals: one commit in history, a name like `migrate_`/`fix_`/`backfill`/`one_off`, no scheduler, CI, package script or doc references it |
| **Duplication** | Near-identical blocks or files that change together |
| **Tracked but ignored** | `git ls-files -ci --exclude-standard` |
| **Untracked or ignored junk** | `git clean -nd` (untracked) and `git clean -ndX` (ignored) are dry runs. Git cannot restore these files, so deleting them is permanent |
| **Stray lines and exports** | Leftover `print`/`console.log`/`debugger`, exports nothing imports. These are edits, not file deletions |

### 2. Verify every candidate
A detector is a lead, not a verdict. Before a candidate reaches the user, check what the tool
cannot see:
- Entry points and framework conventions (routes, plugins, CLI bins, `main` fields, config-driven loaders).
- Dynamic loading: `import(variable)`, reflection, `getattr`, string-built paths.
- Non-code consumers: CI, cron or scheduler definitions, container files, Makefiles, docs, other repos in the fleet.
- Public API: removing an export is a breaking change if anything outside the repo imports it.

Fix false positives by configuring the detector (declare the entry point) before using ignore
lists. An ignore hides a result; it does not resolve it.

No detector installed, or no network? Do it by hand: `git grep -lwF <name>` per candidate, scan
imports and requires, and check scheduler, CI and container files. Do not let `npx` or `pip
install` quietly download a tool; say what you would run and let the user decide.

Treat a dynamic-loading chain as one unit. A plugin loaded by a loader that nothing calls is
orphaned together with its loader; deleting half of it leaves a broken reference.

Give each candidate a confidence: **high** (zero references anywhere, clear temp/debug
pattern), **medium** (zero static references, but dynamic loading is plausible), **low**
(detector only). Only high-confidence items are proposed for deletion without extra discussion;
the rest are questions. History signals (single commit, age) are weak in young or small repos
where every file has one commit: use them to break ties, not as evidence. References from
outside the repo (other projects, deploy hosts) are invisible from here, so when that is
plausible, ask.

### 3. Ask before deleting
Present a table: path, category, evidence, confidence, risk. Group by category. Wait for the
answer. Then delete with `git rm`, **one commit per category** with a message that names what
went and why, so any single group can be reverted. Never run a detector's auto-fix mode that
removes files.

Two cases need extra care. Untracked or ignored files cannot be restored from git: show the
`git clean -nd` output and get explicit approval first. Stray lines and unused exports go in
their own table as edits; an export of a package other projects consume stays unless the user
confirms nothing outside depends on it.

### 4. Dependencies: remove, then refresh
Remove unused ones (after step 3's confirmation). Then check freshness:
- List outdated and vulnerable packages with the ecosystem's own tools (`references/detectors.md`).
- Update in small groups. Patch and minor first; each major bump gets its changelog and
  migration guide read, then a test run. Never use "force" modes that accept major bumps blindly.
- When a library's API changed, check its **current** documentation instead of recalling the old
  API. Use the Context7 MCP if it is connected (it may ask you to authenticate first); otherwise
  open the official docs.
- Commit lockfiles. Applications pin; libraries keep ranges. If there is no lockfile, say so:
  creating one needs an install (network), so ask first.
- Offer to automate this with Dependabot or Renovate (grouped updates, a schedule), so freshness
  stops being a cleanup task.

### 5. Simplify what you touch
Apply KISS and DRY only to code the cleanup already put in play; unrelated refactors belong in a
separate request.
- Remove duplication when the copies change for the same reason. Two similar blocks that change
  for different reasons should stay apart: a wrong abstraction costs more than duplication.
  When you do extract, wait for the third occurrence (Metz, Beck's design rules; see references).
- Names reveal intent; a function name that needs a comment to explain it is the wrong name.
- Comments explain *why* (a constraint, an incident, a trade-off), not *what* the code does.

### 6. Last step: make CLAUDE.md and .gitignore match reality
After the cleanup, the workflow changed, so these two files are likely wrong. Show the changes
as a diff and apply them once approved; keep `CLAUDE.md` in the language it is already written in.
- **.gitignore**: add what the cleanup revealed (build output, caches, env files, tool state,
  OS/editor files); never ignore lockfiles; `git rm --cached` anything already tracked that
  should not be. If a secret was ever committed, revoking it is step one; ignoring it is not a fix.
- **CLAUDE.md**: commands to build, test, run and deploy that actually work now; conventions;
  the real workflow. Keep it under ~200 lines, write checkable instructions ("2-space
  indentation", not "format nicely"), and for each line ask: would removing this cause a mistake?
  Drop anything an agent can read from the code and anything that changes often. Fix every path
  or file it mentions that this cleanup moved or deleted.

### 7. Verify and report
Re-run the baseline build and tests and the detectors. Report: what was removed (counts per
category), what was kept and why, what was deferred to the user, dependency changes, and the
before/after of detector findings. Say plainly if anything is still red.

## Principles

- Smaller is the goal, but never by guessing.
- Separate commits per category; a mixed commit cannot be reverted cleanly.
- If an item is a "maybe", it goes in the questions list, not the deletion list.
