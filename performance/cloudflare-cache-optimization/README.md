# Cloudflare Cache Optimization

Claude Code skill that audits and tunes the Cloudflare caching stack (Cache Rules, Browser TTL, Tiered Cache, Cache Reserve, Serve Stale) to maximise cache hit ratio, cut origin requests and reach sub-50 ms TTFB on cache hits. Marks every recommendation by plan tier so it never suggests a feature the zone cannot use.

## Install

Part of the `hayka-pacha/skills` registry. Clone the registry, then symlink this skill in:

```bash
git clone git@github.com:hayka-pacha/skills.git
ln -s "$(pwd)/skills/performance/cloudflare-cache-optimization" ~/.claude/skills/cloudflare-cache-optimization
```

## Triggers

Cloudflare cache, CDN performance, cache hit ratio, origin shielding, Tiered Cache, Cache Rules, Cache Reserve, edge TTL, TTFB, `cf-cache-status`, or speeding up any site behind Cloudflare (origins, Pages, Workers).

## Structure

```
cloudflare-cache-optimization/
└── SKILL.md   # 4-layer cache model, plan-tier matrix, dashboard + API recipes, audit checklist
```
