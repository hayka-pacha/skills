# Detectors and recipes

Commands are starting points; flags change between versions, so check `--help` or the linked
page when a command errors.

## Contents
- Dead code and unused dependencies by ecosystem
- Git recipes
- Dependency freshness
- .gitignore
- CLAUDE.md
- KISS / DRY
- Not verified

## Dead code and unused dependencies by ecosystem

| Ecosystem | Dead code / files | Unused dependencies |
|---|---|---|
| JS / TS | `npx knip` (`--production` checks only production entry patterns, ignores tests) | knip. depcheck was archived in June 2025; its maintainers point to knip |
| Python | `vulture . --min-confidence 80` | `deptry .` (run inside the project's virtualenv) |
| Go | `deadcode ./...` (`-test` for libraries without `main`) | `go mod tidy -diff` (exits non-zero if changes are needed; fits CI) |
| Rust | none researched | `cargo +nightly udeps`, or `cargo machete` (fast, less precise) |

Sources: https://knip.dev/explanations/entry-files , https://knip.dev/features/production-mode ,
https://github.com/depcheck/depcheck , https://github.com/jendrikseipp/vulture ,
https://deptry.com/usage/ , https://go.dev/blog/deadcode , https://pkg.go.dev/cmd/go ,
https://github.com/est31/cargo-udeps , https://github.com/bnjbvr/cargo-machete

Known false-positive sources per tool:
- **knip** starts from `index`/`main`/`cli` files, `package.json` `main`/`bin`/`exports` and
  scripts, plugin config files and literal dynamic imports. Setting `entry` or `project`
  yourself **replaces** the defaults. Put unresolved dynamic imports in `entry`; use `ignore*`
  "only as a last resort". `--fix` will not delete files unless `--allow-remove-files` is added:
  do not add it. https://knip.dev/guides/handling-issues , https://knip.dev/features/auto-fix
- **vulture** scores confidence: 100% unreachable code and unused arguments, 90% imports, 60%
  everything else. Anything reached through `getattr` or dynamic dispatch is flagged. Prefer a
  whitelist file (`--make-whitelist`) over `--ignore-names` or `noqa`.
- **deptry** rules: DEP001 missing, DEP002 unused (dev dependencies not checked), DEP003
  transitive, DEP004 dev dependency used in production code, DEP005 stdlib declared. Use
  `package_module_name_map` when a package and its module have different names; it misses
  `importlib.import_module(variable)`. https://deptry.com/rules-violations/
- **deadcode (Go)** traces from `main`; code reached only from assembly or `go:linkname` is
  wrongly flagged.
- **cargo-udeps / cargo-machete**: doc-test-only use (udeps), build-script-generated code and
  renamed crates (machete) are mis-flagged. Prefer machete's `renamed` map over `ignored`.

## Git recipes

```bash
git ls-files -ci --exclude-standard              # tracked files that match ignore rules
git grep -lwF <name>                             # tracked files referencing a name (-q for exit code only)
git rev-list --count HEAD -- <file>              # 1 = committed once, never touched again
git log -1 --format=%cs -- <file>                # date of last change
git log --diff-filter=D --name-only --oneline    # what past commits deleted
git log -1 -- <deleted-path>                     # the commit that deleted it (restore from its parent)
```

Not-touched-in-N-months loop: for each tracked file, `git log -1 --since="6 months ago" --format=%H -- <file>`
printing nothing means no change since. Built from documented flags; a heuristic, not a verdict.
Sources: https://git-scm.com/docs/git-log , https://git-scm.com/docs/git-rev-list , https://git-scm.com/docs/git-grep

## Dependency freshness

| Ecosystem | Check | Notes |
|---|---|---|
| npm | `npm outdated`, `npm audit` | "Wanted" = newest within your range, "Latest" = registry `latest` tag. `npm audit fix --force` can install major bumps: avoid. `--audit-level` sets the CI failure threshold |
| Python | `python -m pip list --outdated`, `pip-audit` | `pip-audit --fix --dry-run` first; exit code 1 = vulnerabilities found |
| Go | `go list -m -u all`, `go mod tidy` | |
| Rust | `cargo outdated` (third-party) | `Cargo.lock`: committing is a per-project choice; library consumers ignore it |

Lockfiles: `package-lock.json` "is intended to be committed".
Sources: https://docs.npmjs.com/cli/v11/commands/npm-outdated , https://docs.npmjs.com/cli/v11/commands/npm-audit ,
https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json , https://pip.pypa.io/en/stable/cli/pip_list/ ,
https://github.com/pypa/pip-audit , https://doc.rust-lang.org/cargo/faq.html

Automation:
- **Dependabot** (`version: 2`): per-ecosystem `schedule.interval`; `groups` with `patterns` and
  `update-types`; `versioning-strategy` is `auto`, `increase`, `increase-if-necessary`,
  `lockfile-only` or `widen`. Defaults: 3-day cooldown, 5 open PRs.
  https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference
- **Renovate**: pin dependencies in applications, keep ranges in libraries, lockfile either way
  (https://docs.renovatebot.com/dependency-pinning/). Reduce noise with `packageRules` +
  `groupName`, a `schedule`, automerge for low-risk updates; grouping makes it harder to find
  which update broke the build (https://docs.renovatebot.com/noise-reduction/). `minimumReleaseAge`
  delays fresh releases (https://docs.renovatebot.com/configuration-options/).

## .gitignore

- It only affects untracked files. To stop tracking: `git rm --cached <file>`, then add the rule.
- Scopes: `.gitignore` (shared), `.git/info/exclude` (this clone), `core.excludesFile` (personal).
- A file cannot be re-included with `!` when its parent directory is excluded.
- Starting points: github/gitignore templates (editor and OS rules under `Global/`).
- A committed secret: revoke or rotate first, then purge history with git-filter-repo.

Sources: https://git-scm.com/docs/gitignore , https://git-scm.com/docs/git-rm ,
https://github.com/github/gitignore ,
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

## CLAUDE.md

- Include: build and test commands, conventions, project layout, "always do X" rules. Under 200
  lines. Checkable wording. `@path` imports go at most 4 levels deep and do not reduce context
  cost. `CLAUDE.local.md` is personal and belongs in `.gitignore`. Review periodically and remove
  outdated or conflicting instructions. https://code.claude.com/docs/en/memory
- Test each line: "Would removing this cause Claude to make mistakes?" Leave out what can be
  read from the code and what changes often. Check the file into git. https://code.claude.com/docs/en/best-practices

## KISS / DRY

- "Duplication is far cheaper than the wrong abstraction"; if an abstraction is wrong, inline it
  back into each caller first. https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- Beck's design rules, in order: passes the tests, reveals intention, no duplication, fewest
  elements. https://martinfowler.com/bliki/BeckDesignRules.html
- YAGNI does not apply to work that makes code easier to change. https://martinfowler.com/bliki/Yagni.html
- Rule of three ("use before reuse") is quoted on https://martinfowler.com/articles/practical-test-pyramid.html

## Not verified

- A primary source for the rule of three (Fowler's *Refactoring*, credited to Don Roberts).
- Filename patterns for one-shot scripts: heuristic, no official source.
- An official list of what a `.gitignore` should contain: GitHub gives templates, not a rule set.
- Rust dead-code detection (no tool researched).
