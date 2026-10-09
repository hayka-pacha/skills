---
name: architecture-review
description: >-
  Give a critical, evidence-based opinion on a whole codebase's architecture and delivery
  pipeline: pros and cons, breaking points, what is hard to maintain, manage or monitor, useless
  or nonsensical workflow steps, CI/CD bottlenecks, and a prioritised plan to reduce
  fragmentation, friction and pain points. Use this skill whenever the user asks for a "critical
  opinion", an architecture review or audit, "what's wrong with this setup", a CI/CD workflow
  review, "where are the bottlenecks", "how can I simplify this", or wants a second look at a
  project they have outgrown, even if they never say the word "architecture". Works for any
  language, stack or repo layout, including multi-repo setups where several projects share one
  template.
metadata:
  version: 1.0.0
---

# Architecture Review

Produce an honest assessment the owner can act on. Flattery wastes their time and a vague
"consider refactoring" is just as useless: every claim needs evidence from the code, config or
logs, and every recommendation needs its tradeoff.

Read-only by default. Propose changes; do not apply them, and never delete anything without
asking first. Evidence may be reproduced cheaply (run the tests, simulate a failing dependency)
but only in a scratch copy, never in the target repository. Answer in the user's language.

## Workflow

### 1. Map before judging
Read the whole project, not a sample. Build a one-page mental model and keep it for the report:
- Entry points, main modules, data stores, external services and the direction of every dependency.
- How code reaches production: build, test, deploy, scheduling, secrets, config per environment.
- Every automation file: CI workflows, scripts, cron or scheduler definitions, container files.
- Where state lives and what happens when a run is interrupted halfway.

Use `git log` for history when a decision looks strange. A weird choice is often a scar from an
old incident, and saying so makes the review fairer and more useful.

### 2. Trace the real workflow end to end
Follow one unit of work from trigger to final outcome and write the steps down. Mark each step as
**needed**, **redundant**, or **unknown**. Nonsensical logic usually shows up here: a step that
undoes the previous one, a check that can never fail, a manual hop between two automated stages,
the same fact configured in three places.

### 3. Evaluate against the pillars
Use the checklist in `references/checklist.md` (Reliability, Security, Operational excellence,
Performance, Cost, Sustainability, plus CI/CD hygiene and delivery metrics). Skip pillars that
do not apply and say so in one line, rather than padding.

### 4. Audit CI/CD specifically
Walk each pipeline for missing timeouts, no concurrency control, unpinned third-party actions,
broad token permissions, cache keys that never hit, steps that run on every change though only
some paths matter, duplicated workflows that could be one reusable definition, stages
serialised without reason, and deploy jobs that run on every branch. Some failures are visible
by reading alone (a test command that finds no tests, a script that is not executable in git):
report them directly. If run history is available (a remote with recent runs), hand the
analysis of failing runs to the `ci-failure-analysis` skill instead of guessing at causes.

### 5. Use logs when they exist
Logs turn opinions into evidence. Look for repeated errors, retry storms, long gaps between
steps, and steps that dominate the elapsed time. If the question is *how long things take and how
to speed them up*, use the `pipeline-throughput-analysis` skill, which has a script for it.

### 6. Report
Use this structure, in this order. Start with a short scope note: what you read, what you ran
and where, what you could not see, and which pillars you skipped because they do not apply.

1. **Verdict** (3 to 5 lines): what the architecture is good at, and the single biggest risk.
2. **What works** (pros): only things you verified, each with where.
3. **Breaking points**: what fails first and why, ranked by severity × likelihood (high /
   medium / low for each; severity is the damage if it happens, likelihood is how soon it
   will). For each: evidence (`path:line` or log excerpt), failure scenario, blast radius.
4. **Hard to maintain / manage / monitor**: separate sub-lists. For monitoring, say what you
   could not tell from the repo alone (no health signal, no alert, logs without ids).
5. **Workflow waste**: the step-2 trace table (needed / redundant / unknown) and the time or
   effort each wasted step costs. Include the fragmentation count: facts that must be edited
   in more than one place.
6. **Plan**: three tiers (**now**: cheap and safe; **reduce fragmentation**: remove moving
   parts; **only if scale demands**), each item with effort (S/M/L), the tradeoff of doing it,
   and what it removes (a file, a step, a manual action). Prefer changes that *remove* moving
   parts over changes that add tooling. Fewer places to edit beats a smarter system to edit them
   in. Flag ordering dependencies: when fixing one item first would make another dangerous
   (for example making a deploy script runnable before gating the job that runs it), say so.
7. **Open questions**: things only the owner can answer (intended scale, who operates it, what
   an outage costs).

Offer to record accepted decisions as Architecture Decision Records. Append-only: a changed
decision gets a new record that supersedes the old one.

## Calibration rules

- Say "I could not verify" instead of guessing. Unverified criticism erodes trust in the rest.
- Distinguish *wrong* from *different from what I'd do*. Only the first is a finding.
- Weigh the project's size. A solo-maintained tool does not need an enterprise control plane;
  recommending one is a failure of judgement, not thoroughness.
- Every recommendation names what it costs. If you cannot name a cost, you have not thought
  about it enough.
- Count the places a single fact must be edited. More than one is fragmentation worth reporting.
