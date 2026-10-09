---
name: docs-consolidation
description: >-
  Make a repository's documentation strictly consistent with its code and reduce it to one
  technical README.md at the root and one PRODUCT-SPECS.md in docs/, merging what is worth keeping
  from every other Markdown file and proposing the rest for deletion after confirmation. Checks
  every documented command, path, link and environment variable against the code, and protects
  files that tools require (CLAUDE.md, SKILL.md, LICENSE, CHANGELOG and community health files).
  Use this skill whenever the user wants docs cleaned up, merged, de-duplicated or brought back in
  sync with the code, complains about scattered or outdated .md files, asks for a README or
  product spec rewrite, or wants "one source of truth" for documentation, even if they only say
  "the docs are a mess".
metadata:
  version: 1.0.0
---

# Docs Consolidation

Documentation that disagrees with the code is worse than none: readers trust it and get hurt.
Scattered documentation drifts faster, because every extra file is another place to forget.
The target is two files that are small enough to keep true:

- **`README.md`** (repo root): technical. How to install, configure, run, test, deploy; the
  architecture in brief; the commands that actually work.
- **`docs/PRODUCT-SPECS.md`**: product. What the system does for whom, its rules and
  behaviours, what is out of scope.

If the user names other files or paths, use theirs; the logic is identical. Deleting a file needs
the user's confirmation, always: show the plan, wait, then delete with `git rm` (history keeps it).

## Workflow

### 1. Inventory
Run `python3 <this-skill-folder>/scripts/check_docs.py <repo-root>`. It sorts every `.md` (and
bare `LICENSE`/`COPYING`/`NOTICE` files) into:
- **keep**: the two target files.
- **protected**: never merge or delete. `CLAUDE.md` (and any file it imports with `@path`),
  `SKILL.md` and everything in that skill's folder, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING`,
  `SECURITY`, `CODE_OF_CONDUCT`, `SUPPORT`, issue/PR templates, anything under `.github/` or
  `.claude/`. Tools and platforms look for these by name.
- **candidate**: everything else. These are the files to merge or retire.

It also flags README files that shadow each other (GitHub shows `.github/` first, then root,
then `docs/`, so a stray one hides the root README), broken links, documented paths that match
no file, `npm run` scripts and `make` targets that do not exist, environment variables that
exist only on one side, and keepers or protected files that still point at a candidate. It does
not run commands or understand other task runners: step 6 covers the rest by hand.

Protected means *do not merge or delete*. Fixing a stale path or pointer inside a protected
file (for example a `CLAUDE.md` line that names a file you are removing) is expected: show it
as a diff with the rest of the plan.

### 2. Establish the truth from the code
The code and config are the source of truth, not the old docs. Extract what is real: scripts and
commands (package scripts, Makefile, CI), entry points, ports, environment variables, config
keys, directory layout, versions, and the behaviours the code implements. Where a doc claims
something you cannot find in the code, treat the doc as wrong until shown otherwise.

### 3. Decide where each fact lives
Use the distinction Diátaxis draws between kinds of documentation: mixing them "is at the heart
of a vast number of problems":

| Content | Home |
|---|---|
| Install, run, test, deploy, configure; commands; env vars; architecture sketch | README |
| What the product does, for whom; rules; behaviours; requirements; out of scope | PRODUCT-SPECS |
| Why a decision was made | one line in the relevant file, or an ADR if the project keeps them |
| History of changes | CHANGELOG (protected), not the README |
| Features the docs claim but the code does not implement | Do not document them as existing. Tell the user, who decides: drop them, or keep one dated line under "Open questions" |
| Wishes and plans | neither. Document what the code does today |

Duplicated facts get one home and a link from the other place. Reference material that can be
generated from code should be, so it cannot drift.

### 4. Merge, then propose deletions
For each candidate file: extract what is still true and valuable, draft it into its home, and
note where it went. Then present the drafts and a table: file, verdict (merged into X /
duplicate of X / obsolete), and what, if anything, was lost on purpose. **Stop and wait for
confirmation.** Nothing is deleted or overwritten before the user approves; after approval,
write the two files, then `git rm` the candidates.

### 5. Write the two files
Use the skeletons in `references/templates.md`. House rules, from Google's developer
documentation style guide: address the reader as "you", active voice, conditions before
instructions, sentence-case headings, code in code font, numbered lists for sequences, descriptive
link text, and no announcing of future features. Short beats thorough: a README should contain
only what a developer needs to get started and contribute; longer material is linked.
Never invent a command, flag, number or behaviour. If you cannot verify it, leave it out or
ask. Keep only the sections that apply; an empty section is padding. Write in the language the
repository's existing docs use, and reply to the user in theirs.

### 6. Verify
- Re-run `scripts/check_docs.py`: broken links, dead paths and env-var mismatches should be gone.
- Run the commands the README tells readers to run (install, build, test at least) in a clean
  checkout or a scratch copy, and fix the docs, not the commands, when they disagree.
- If `lychee` is available, `lychee --offline .` checks local links (add `--include-fragments`
  for anchors); `markdownlint` catches structure problems.
- Fix pointers elsewhere: `CLAUDE.md` imports, CI steps, package metadata and code comments that
  reference a deleted file.

### 7. Keep it true
Offer to add the cheap guards: a CI step that runs link checking and `check_docs.py`, and a
rule in the contributing notes that a change which alters behaviour or commands updates the
README or specs in the same pull request.

## Output

1. Inventory (keep / protected / candidate counts).
2. Disagreements found between docs and code, each with the file and the evidence.
3. Drafts, merge plan and deletion proposal, with the questions that need an answer, awaiting
   confirmation.
4. After approval: the two files, the deletions, and the verification results.
