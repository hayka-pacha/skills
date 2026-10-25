# hayka-pacha/skills

Open registry of reusable `SKILL.md` packages for Claude Code and other agents. Each skill lives in `<domain>/<skill-name>/` and is published to [Smithery](https://smithery.ai/skills/hayka-pacha) automatically on every push to `main`.

## Skills

| Domain | Skill | What it does |
|---|---|---|
| `seo/` | [seo-growth-engine](seo/seo-growth-engine/) | Structured 7-phase SEO audit and fix plan, backed by 60+ sources |
| `seo/` | [geo-audit-optimization](seo/geo-audit-optimization/) | Generative Engine Optimization: visibility and citations in ChatGPT, Perplexity and other AI answers |
| `seo/` | [geo-affiliation](seo/geo-affiliation/) | GEO for affiliate publishers: audit cited pages, improve comparisons and measure referrals |
| `performance/` | [cloudflare-cache-optimization](performance/cloudflare-cache-optimization/) | Audit and tune the Cloudflare cache stack for hit ratio, TTFB and origin load |
| `performance/` | [pipeline-throughput-analysis](performance/pipeline-throughput-analysis/) | Mine pipeline or bot logs for where time goes and how to meet a per-batch time budget |
| `codebase/` | [codebase-cleanup](codebase/codebase-cleanup/) | Find debug, orphaned, dead and one-shot code and unused dependencies; delete only after confirmation |
| `codebase/` | [architecture-review](codebase/architecture-review/) | Critical, evidence-based architecture and CI/CD review with a prioritised plan |
| `codebase/` | [docs-consolidation](codebase/docs-consolidation/) | One README, one product spec, docs verified against the code |
| `ci-cd/` | [ci-failure-analysis](ci-cd/ci-failure-analysis/) | Root-cause CI/CD failures and recommend permanent fixes, not workarounds |
| `ebooks/` | [comic-to-kindle](ebooks/comic-to-kindle/) | Convert CBZ/CBR/PDF comics for Kindle, Kobo or reMarkable with Kindle Comic Converter, then verify the output |
| `youtube/` | [affiliation-facile-youtube-storytelling](youtube/affiliation-facile-youtube-storytelling/) | Scripts originaux YouTube pour débutants en affiliation, avec preuves et transparence commerciale |

## Install a skill

Clone the registry once, then symlink the skills you want into Claude Code's skills folder:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/ebooks/comic-to-kindle" ~/.claude/skills/comic-to-kindle
```

Or install from Smithery: `https://smithery.ai/skills/hayka-pacha/<skill-name>`.

## Layout

```
<domain>/
└── <skill-name>/
    ├── SKILL.md          # required: frontmatter (name, description) + instructions
    ├── README.md         # what it does, install, structure
    ├── scripts/          # optional: executable helpers
    ├── references/       # optional: docs loaded on demand
    └── evals/evals.json  # optional: test prompts and expectations
```

Domains are plain words describing the problem area (`seo`, `performance`, `ebooks`, `codebase`, `ci-cd`). Add a new one when no existing domain fits; do not use generic buckets.

## Publishing

`.github/workflows/publish-smithery.yml` runs on every push to `main` that touches a `SKILL.md`. It publishes each changed skill under the slug `hayka-pacha/<skill-name>` (the folder name) with the skill's GitHub URL. Moving a skill to another domain re-publishes it with the new URL; the slug does not change.
