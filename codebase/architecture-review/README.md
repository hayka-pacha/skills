# Architecture Review

Claude Code skill that reads a whole codebase and gives a critical, evidence-based opinion: strengths, breaking points, what is hard to maintain, manage or monitor, useless or nonsensical workflow steps, CI/CD bottlenecks, and a prioritised plan to cut fragmentation and friction. Every claim cites a file or log; every recommendation states its tradeoff.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/codebase/architecture-review" ~/.claude/skills/architecture-review
```

## Triggers

Critical opinion on an architecture; architecture or CI/CD review; "where are the bottlenecks"; "how can I simplify this"; pros and cons of a setup; reducing fragmentation across scripts, workflows and repos.

## Structure

```
architecture-review/
├── SKILL.md                    # map, trace, evaluate, audit CI/CD, use logs, report
├── references/checklist.md     # well-architected pillars, failure modes, operability, CI/CD hygiene, DORA, ADRs
└── evals/evals.json            # test prompts and expectations
```

Hands off to `ci-failure-analysis` for failing runs and to `pipeline-throughput-analysis` for timing questions.
