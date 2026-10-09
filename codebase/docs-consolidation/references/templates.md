# Skeletons and sources

## Contents
- README skeleton
- PRODUCT-SPECS skeleton
- Protected files
- Tooling for keeping docs honest
- Sources
- Not verified

## README skeleton

Keep only sections that apply. Everything must be verifiable against the code.

```markdown
# <Project name>

<One or two sentences: what it is and why it exists.>

## Requirements
<Runtimes and tools with versions, copied from the version files or CI, not from memory.>

## Setup
<Numbered commands that work from a fresh clone.>

## Configuration
| Variable | Required | Purpose |
|---|---|---|

## Run
<Dev, production, scheduled jobs: the real commands.>

## Test
<How to run the tests and what "green" means.>

## Architecture
<Short description of the main parts and how data moves; a diagram only if it earns its place.>

## Deploy
<How code reaches production; where CI lives.>

## Where to read more
- [Product specs](docs/PRODUCT-SPECS.md)
```

## PRODUCT-SPECS skeleton

Adapted from the sections of a product requirements template (objective and success metrics,
assumptions, requirements, open questions, out of scope), dropping release dates and team roles
because this file describes the product as it behaves today.

```markdown
# Product specs

## Purpose
<The problem solved, for whom, and how success is measured.>

## Users and use cases
<Who uses it and what they do.>

## Behaviour and rules
| Requirement | Behaviour as implemented | Notes |
|---|---|---|

## Key flows
<Step-by-step description of the main end-to-end flows.>

## Constraints and assumptions
<Limits, dependencies on external services, data rules.>

## Open questions
<Unresolved items, with dates.>

## Out of scope
<What the product deliberately does not do.>
```

## Protected files

Never merge or delete these without an explicit request:

| File | Why |
|---|---|
| `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md` | Loaded by agents by name. Any file `CLAUDE.md` imports with `@path` is loaded too. Aim for under 200 lines. https://code.claude.com/docs/en/memory |
| `SKILL.md` and its folder | The skill's referenced files are part of the skill. Keep `SKILL.md` under 500 lines. https://code.claude.com/docs/en/skills |
| `CODE_OF_CONDUCT`, `CONTRIBUTING`, `SECURITY`, `SUPPORT`, `ACCESSIBILITY`, `FUNDING.yml`, issue/PR templates | GitHub community health files; may live in root, `.github/` or `docs/`. `FUNDING.yml` and the vulnerability-report form must be in `.github/`. https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file |
| `LICENSE` | Detected by name at the root; without it default copyright applies. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository |
| `CHANGELOG.md` | For humans; `Unreleased` at the top; groups Added, Changed, Deprecated, Removed, Fixed, Security. Dumping the git log is a bad idea. https://keepachangelog.com/en/1.1.0/ |

## Tooling for keeping docs honest

- **lychee**: checks links in Markdown and HTML; `--offline` for local files, `--include-fragments`
  for anchors; has a GitHub Action. https://github.com/lycheeverse/lychee
- **markdown-link-check**: checks that links are alive; `ignorePatterns`. https://github.com/tcort/markdown-link-check
- **markdownlint** (CLI: markdownlint-cli2): CommonMark/GFM rules MD001 and up, configured in
  `.markdownlint.json/.jsonc/.yaml`. https://github.com/DavidAnson/markdownlint
- **Executable docs**: Python `doctest` verifies that interactive examples still work.
  https://docs.python.org/3/library/doctest.html
- Docs as code: version control, plain text, review and automated tests; "you can block merging
  of new features if they don't include documentation." https://www.writethedocs.org/guide/docs-as-code/
- Doc and code drift in practice: pull env vars, flags, scripts, paths and ports out of the docs
  and check each against the code. Documentation-only matches are stale; code-only matches are
  undocumented. `scripts/check_docs.py` automates the first pass. (This is the skill's own method;
  no source prescribes it.)

## Sources

- GitHub README guidance (content, location precedence `.github/` > root > `docs/`, truncation
  beyond 500 KiB, relative links, automatic table of contents):
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Diátaxis (tutorial, how-to, reference, explanation): https://diataxis.fr/start-here/ and
  https://diataxis.fr/reference/ . Reference should mirror the product's structure and be
  generated from code where possible. Mapping README vs specs is this skill's reading, not
  Diátaxis's.
- Google developer documentation style guide: https://developers.google.com/style ,
  highlights https://developers.google.com/style/highlights
- Product requirements template (Atlassian): https://www.atlassian.com/software/confluence/templates/product-requirements

## Not verified

- An official convention for a file called `PRODUCT-SPECS.md`: that name is a project policy.
- markdown-link-check's handling of anchors and whether it is still maintained.
- A primary source for running README commands in CI.
- Whether GitHub's licensing page accepts a bare `LICENSE` with no extension (it names
  `LICENSE.txt`, `.md`, `.rst`).
