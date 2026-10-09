---
name: fleet-drift-audit
description: >-
  Detect and resolve drift between a shared source of truth (a template, factory, base repo or
  shared package) and the many projects derived from it, so every one of them follows the same
  workflow. Compares files, scripts, CI workflows, configs and dependency versions across repos,
  classifies each difference (intentional, stale, worth upstreaming, bug), and recommends what to
  do. Use this skill whenever the user mentions drift, child, derived or downstream repos or sites
  that diverge from a base, keeping several repos in sync, "the same workflow must apply to all of
  them", template or boilerplate updates that never reached the copies, monorepo-lite fleets, or
  a consistency check across projects, even if they never use the word "drift".
metadata:
  version: 1.0.0
---

# Fleet Drift Audit

One source of truth, many copies. Copies drift because fixing the copy in front of you is always
faster than fixing the source and propagating. This skill finds the drift, decides what each
difference *is*, and makes the next drift cheaper to catch.

Report first, change nothing. Apply a fix only after the user agrees, and ask before any
deletion, even of a file that looks obviously stale.

## Workflow

### 1. Establish the fleet
Confirm with the user, or find in the repo (registry file, CI matrix, submodules, a list in docs):
- **Source of truth**: path or remote, and the ref the fleet is supposed to follow. With no tag
  or tracking file, use the source's current HEAD and say so; if the question is "which copies
  are stale", git history shows when each copy last matched the source.
- **Derived projects**: the full list. A missing member is itself a finding.
- **What is supposed to be shared**: workflow, scripts, CI, config shape, dependency baseline.

Audit derived projects one at a time when they share state a tool can leak between runs (browser
sessions, ports, caches, credentials). Parallel runs hide which project produced which result.

### 2. Sort every path into three buckets
Propose the buckets yourself from the user's wording and the repo layout, then carry on with
the read-only audit; list "are these buckets right?" as the first question in the report. Asking
first would block a simple "check and tell me" request, and the audit itself changes nothing.
The buckets turn raw diffs into verdicts.

| Bucket | Meaning | Drift means |
|---|---|---|
| **Must match** | Logic, CI, scripts, tooling config | Almost always a defect |
| **Parametrised** | Same shape, values differ (names, URLs, IDs, per-project flags) | Only the *shape* can drift |
| **Local only** | Content that is the point of the project | Not drift |

If many files sit in "must match" yet legitimately differ, that is a design smell: the shared
logic is forked, not parametrised. Report it as the finding.

### 3. Measure
Run `python3 <this-skill-folder>/scripts/drift_matrix.py SOURCE DERIVED...` for the file-level
matrix (identical, differs, missing, extra per project; exit code 1 on any drift). Run it per
bucket: `--only <globs>` for the must-match paths, `--shape <globs>` for parametrised JSON config
(compares key structure, so different values show as `~=` and are not drift), `--ignore <globs>`
for local-only content. Then go beyond bytes:
- Dependency and runtime versions (lockfiles, tool versions) against the baseline.
- CI workflow *structure*: same jobs, same order, same triggers, same permissions and timeouts.
- Script behaviour: two scripts with the same name and different contents are the classic trap.
- Config *keys*: a derived project that lacks a new key silently falls back to a default.
- Everything one project has that others do not: possible upstream material, or leftover junk.
- Problems the whole fleet inherits from the source (a script calling a file that exists
  nowhere, a job that cannot pass). The matrix cannot see them because every copy agrees.
  Report them separately as "outside drift".

### 4. Classify each difference
Use history, not guesses: `git log --follow -- <file>` in both repos, and `git diff <ref> -- <path>`
against the source.

| Class | Typical evidence | Action |
|---|---|---|
| **Stale copy** | Source changed after the copy was made; derived side untouched since | Sync from source |
| **Local improvement** | Derived side is newer and better | Upstream it, then sync the rest |
| **Intentional override** | Commit message or comment explains why | Record it; move it to "parametrised" if repeated |
| **Defect** | Neither side intended it (typo, half-applied change, wrong constant) | Fix at the source if shared, else locally |
| **Unknown** | No evidence either way | Ask the user. Do not pick silently |

The taxonomy is a working heuristic, not an official standard. Say so when presenting it.

### 5. Recommend
For each difference give the class, the evidence, the proposed action and its blast radius.
Group repeated differences ("11 of 14 projects have the stale lint step") into one line.
Prefer fixing the *mechanism* over repeating the fix. See `references/sync-mechanisms.md`: if a
file must always be identical, stop copying it and reference it instead (reusable workflow,
shared package, template-update tool). A fleet of 14 with one reusable workflow has one place to edit.

### 6. Apply, only when told to
Make source changes first, then propagate. Re-run the matrix afterwards and show the before and
after counts. If a derived project has local work in progress, stop and ask.

## Output

1. Fleet summary: source, ref, members audited, members skipped and why.
2. Drift matrix, drifted rows only.
3. Findings table: path, class, evidence, action, blast radius.
4. Root cause: why this fleet drifts (copy-paste distribution, no update path, no CI check).
5. Prevention plan: smallest mechanism that removes the cause, plus a CI check that fails on drift.
6. Questions for the user: whether the buckets are right, every "unknown", and every deletion or
   overwrite you would need approval for. Nothing is applied until they answer.
