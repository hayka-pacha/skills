# SEO Growth Engine

Complete SEO audit & optimization skill for Claude Code. 60+ authoritative sources (Google, Ahrefs, Moz, Backlinko, web.dev).

## Install

```bash
claude plugins install git@github.com:hayka-pacha/seo-growth-engine.git
```

Or manually:

```bash
git clone https://github.com/hayka-pacha/seo-growth-engine.git ~/.claude/skills/seo-growth-engine
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

Produces a structured audit report with severity-ranked findings and a priority action plan.

## Structure

```
seo-growth-engine/
├── SKILL.md              # Workflow (triggers on SEO-related prompts)
└── references/
    ├── benchmarks.md     # CWV thresholds, schema tables, conversion benchmarks
    └── sources.md        # 64-source bibliography
```

## Triggers

The skill auto-triggers on: SEO audit, traffic drop diagnosis, Core Web Vitals, page speed, Google ranking, indexation issues, sitemaps, structured data, hreflang, international SEO, affiliate SEO, programmatic SEO, content strategy, E-E-A-T, conversion optimization, internal linking.
