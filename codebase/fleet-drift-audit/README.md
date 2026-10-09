# Fleet Drift Audit

Claude Code skill that compares a source of truth (template, factory, base repo) with the projects derived from it, classifies every difference (stale copy, local improvement, intentional override, defect, unknown) using git history, and recommends the mechanism that stops the drift from coming back. Report first; nothing is changed or deleted without agreement.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/codebase/fleet-drift-audit" ~/.claude/skills/fleet-drift-audit
```

## Triggers

Drift between a base repo and derived repos or sites; keeping several projects on the same workflow; template updates that never reached the copies; copy-pasted CI across repos; a consistency check across a fleet.

## Structure

```
fleet-drift-audit/
├── SKILL.md                         # fleet, buckets, measure, classify, recommend, apply
├── scripts/drift_matrix.py          # file-level matrix, CI-friendly exit code, --selftest
├── references/sync-mechanisms.md    # reusable workflows, Copier, Cruft, Renovate presets, sources
└── evals/evals.json                 # test prompts and expectations
```

```bash
python3 scripts/drift_matrix.py path/to/base path/to/service-a path/to/service-b
```
