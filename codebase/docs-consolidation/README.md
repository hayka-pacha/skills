# Docs Consolidation

Claude Code skill that makes a repository's documentation strictly consistent with its code: one technical `README.md` at the root and one `docs/PRODUCT-SPECS.md`, with every other Markdown file merged where it still has value and proposed for deletion after confirmation. Checks documented commands, paths, links and environment variables against the code, and protects files that tools require (`CLAUDE.md`, `SKILL.md`, `LICENSE`, `CHANGELOG.md`, community health files).

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/codebase/docs-consolidation" ~/.claude/skills/docs-consolidation
```

## Triggers

Scattered or outdated `.md` files; merge or de-duplicate docs; docs out of sync with the code; rewrite a README or a product spec; "one source of truth" for documentation.

## Structure

```
docs-consolidation/
├── SKILL.md                    # inventory, truth from code, placement, merge, write, verify, keep true
├── scripts/check_docs.py       # keep/protected/candidate inventory, link/path/env-var checks, --selftest
├── references/templates.md     # README and PRODUCT-SPECS skeletons, protected files, tooling, sources
└── evals/evals.json            # test prompts and expectations
```

```bash
python3 scripts/check_docs.py path/to/repo
```
