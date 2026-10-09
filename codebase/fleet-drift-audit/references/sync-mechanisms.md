# Keeping a fleet in sync

Pick the mechanism that leaves the fewest copies. Order of preference: reference > update tool > manual sync.

## Contents
- Reference instead of copy
- Template update tools
- Shared dependency and config baselines
- Detecting drift in CI
- Command cheat-sheet
- Not verified

## Reference instead of copy

**GitHub reusable workflows**: declare `on: workflow_call`, call at job level with
`uses: owner/repo/.github/workflows/file.yml@ref`, pass `with:` inputs and `secrets:`. Up to 10
levels of nesting. Pin to a commit SHA: the docs call it the safest option.
https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows

**Composite actions**: `action.yml` with `runs.using: composite` bundles steps into one step.
Reference as `uses: OWNER/repo@SHA` and tag releases.
https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action

**Organisation rulesets**: "Require workflows to pass before merging" forces a workflow on
selected repos (it replaces the older "required workflows"). Supports `pull_request`,
`pull_request_target` and `merge_group` events only; event filters are ignored; has an evaluate
(dry-run) mode.
https://docs.github.com/en/enterprise-cloud@latest/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets

**GitLab**: `include:` supports `local`, `project`, `remote`, `template`; the including file is
merged last and wins; hashes deep-merge but arrays (`script`, `rules`) are replaced, not merged.
https://docs.gitlab.com/ci/yaml/includes/ . CI/CD components take validated `spec:inputs`; pin to
a SHA or release tag, because `~latest` may bring breaking changes.
https://docs.gitlab.com/ci/components/

## Template update tools

A GitHub template repository does not keep a link to its template: the new repo starts with a
single commit and an unrelated history, so you cannot merge changes back.
https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template

**Copier**: `copier update` regenerates from the template, diffs against the project and
re-applies local changes. Needs a valid `.copier-answers.yml` (never hand-edit it; it stores the
template ref as `_commit`), a template versioned with Git tags, and a clean `git status`.
`copier check-update --quiet` exits 0 when current, 2 when an update exists. Legitimate
divergence: `_skip_if_exists` (file is created once, then left alone), `_exclude`.
https://copier.readthedocs.io/en/stable/updating/ and https://copier.readthedocs.io/en/stable/configuring/

**Cruft**: `cruft check` exits 1 when the project is behind (made for CI); `cruft diff --exit-code`
fails on any local divergence; `cruft update` previews before applying; `cruft link` attaches an
existing Cookiecutter project. `.cruft.json` stores `template`, `commit` and a `skip` glob list.
https://cruft.github.io/cruft/

**Cookiecutter alone** has no documented way to update an existing project (replay only reuses
answers to create a new one). https://cookiecutter.readthedocs.io/en/stable/advanced/replay.html

## Shared dependency and config baselines

**Renovate**: `"extends": ["github>org/repo"]` or `local>org/renovate-config` with a
`default.json`; pin a preset version with `#1.2.3`. https://docs.renovatebot.com/config-presets/

**Dependabot**: organisation settings can enable security updates for all repos, but
`dependabot.yml` is per repository and no `extends` key was found.
https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference

**Repository settings as code**: safe-settings resolves repo > sub-org > org from an admin repo
and re-syncs drift on a webhook or schedule. Community project, not a supported GitHub product.
https://github.com/github-community-projects/safe-settings

## Detecting drift in CI

- `git diff --no-index A B` compares two filesystem paths and implies `--exit-code`;
  `git diff <commit> -- <path>` compares the working tree with any commit; `--quiet`,
  `--name-status`, `--stat` help. https://git-scm.com/docs/git-diff
- `git log --follow -- <file>` follows history past renames (one file only). https://git-scm.com/docs/git-log
- `conftest test --combine a.yaml b.yaml` puts all files into one `input` array so a policy can
  assert across files; `--fail-on-warn` exits 1 on warnings. https://www.conftest.dev/options/
- `scripts/drift_matrix.py` (this skill) gives the file-level matrix with a CI-friendly exit code.

## Command cheat-sheet

```
copier check-update --quiet            # 0 current, 2 update available
copier update --defaults [--conflict rej] [--vcs-ref=HEAD]
cruft check                            # 1 = out of date
cruft diff --exit-code                 # non-zero if local diverges from template
git fetch <template-remote> && git diff <template-ref> -- <path>
git diff --no-index --name-status tmpl/ derived/
git log --follow -- <file>
```

## Not verified

- Whether a ruleset workflow rule can pin to a ref or SHA.
- GitLab `include:project` pinned to a tag or SHA (docs only show `ref: main`).
- Any shared or inherited `dependabot.yml`.
- The stale / improvement / override / defect taxonomy and the "hash manifest of must-match
  files" approach are heuristics of this skill, not documented standards. The nearest official
  signals are Copier `_skip_if_exists`, Cruft `skip`, and GitLab's "local file wins" merge.
