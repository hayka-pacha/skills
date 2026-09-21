# SEO Growth Engine

Complete SEO audit & optimization skill for Claude Code. 60+ authoritative sources (Google, Ahrefs, Moz, Backlinko, web.dev).

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/seo/seo-growth-engine" ~/.claude/skills/seo-growth-engine
```

## What it does

Runs a structured 7-phase SEO audit:

1. **Technical Health** — crawlability, CWV, structured data, meta tags, URLs
2. **Content & On-Page** — E-E-A-T, headings, internal linking, image SEO
3. **International SEO** — hreflang, locale strategy, localization vs translation
4. **Programmatic SEO** — thin content risk, crawl budget, pagination
5. **Affiliate & Monetization** — link best practices, value-add assessment
6. **Conversion** — CTA placement, mobile-first, trust signals
7. **Quick Wins & Monitoring** — GSC formula, monitoring cadence

Reads only the reference(s) matching the user's actual situation — never all seven at once.

## Structure

```
seo-growth-engine/
├── SKILL.md                       # Workflow: which reference(s) to read, response shape, core thresholds
├── scripts/
│   └── audit.py                   # stdlib-only single-page technical SEO audit
├── evals/
│   └── evals.json                 # skill quality evals
└── references/
    ├── phase-1-technical.md
    ├── phase-2-content.md
    ├── phase-3-international.md
    ├── phase-4-programmatic.md
    ├── phase-5-affiliate.md
    ├── phase-6-conversion.md
    ├── phase-7-monitoring.md
    ├── pitfalls.md
    ├── audit-script.md            # audit.py usage
    └── sources.md                 # 60+ source bibliography
```

## Triggers

The skill auto-triggers on: SEO audit, traffic drop diagnosis, Core Web Vitals, page speed, Google ranking, indexation issues, sitemaps, structured data, hreflang, international SEO, affiliate SEO, programmatic SEO, content strategy, E-E-A-T, conversion optimization, internal linking.
