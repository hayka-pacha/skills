# Codebase Cleanup

Claude Code skill that scans a repository for debug files, temporary files, orphaned files, dead code, unused dependencies, one-shot scripts and duplication, verifies every candidate before proposing it, and removes nothing without confirmation. Then refreshes dependency versions from their official docs and brings `CLAUDE.md` and `.gitignore` back in line with the real workflow.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/codebase/codebase-cleanup" ~/.claude/skills/codebase-cleanup
```

## Triggers

Clean up, tidy, prune or audit a repo; dead code; unused files or dependencies; outdated dependencies; KISS and DRY; "the codebase feels messy"; a `CLAUDE.md` or `.gitignore` that has gone stale.

## Structure

```
codebase-cleanup/
├── SKILL.md                 # baseline, inventory, verify, confirm, deps, simplify, sync, report
├── references/detectors.md  # per-ecosystem detector commands, git recipes, dependency tooling, sources
└── evals/evals.json         # test prompts and expectations
```
