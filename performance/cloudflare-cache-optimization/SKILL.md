---
name: cloudflare-cache-optimization
description: Audit and optimize Cloudflare caching configuration for maximum cache hit ratio and minimum origin requests. Use this skill whenever the user mentions Cloudflare cache, CDN performance, cache hit ratio, origin shielding, Tiered Cache, Cache Rules, Cache Reserve, edge TTL, or wants to speed up a site behind Cloudflare. Also triggers on audit requests about page speed, TTFB, origin load reduction, or "cf-cache-status" for Cloudflare-proxied domains. Works for all CF setups: traditional origins, Cloudflare Pages, and Workers.
version: 1.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloudflare, cache, cdn, performance, seo, audit, origin-shielding, nextjs]
    related_skills: []
---

# Cloudflare Cache Optimization

Audit and optimize Cloudflare's caching stack to maximize cache hit ratio, minimize origin requests, and achieve sub-50ms TTFB on cache HITs.

## Why this matters

By default, Cloudflare does NOT cache HTML or JSON. Most sites behind Cloudflare leave massive performance on the table. The difference between default and optimized can be 10x in origin load and 5x in TTFB. For SEO, TTFB is a Core Web Vital signal — cached pages at <50ms vs uncached at 130-300ms directly impacts rankings.

## Architecture: The 4-Layer Cache Stack

```
Visitor → Edge (lower-tier) → Upper-tier → Cache Reserve (R2) → Origin
```

| Layer | What it does | Plan required |
|-------|-------------|---------------|
| **Browser Cache** | Eliminates redundant requests from repeat visitors | Free |
| **Edge Cache** | Serves cached content from the nearest CF datacenter | Free (Cache Rules) |
| **Tiered Cache** | Reduces which datacenters can contact origin | Pro+ |
| **Cache Reserve** | Persistent R2-backed cache, survives edge eviction | Pro+ (usage-based) |

## Free vs Pro Features

Mark each audit item by plan tier so you don't recommend unavailable features:

| Feature | Free | Pro ($20/mo) | Biz ($200/mo) | Enterprise |
|---------|------|-------------|---------------|------------|
| Cache Rules | ✅ | ✅ | ✅ | ✅ |
| Browser TTL override | ✅ | ✅ | ✅ | ✅ |
| Serve Stale | ✅ | ✅ | ✅ | ✅ |
| Smart Tiered Cache | ❌ | ✅ | ✅ | ✅ |
| Cache Reserve | ❌ | ✅ | ✅ | ✅ |
| Polish (image opt) | ❌ | ✅ | ✅ | ✅ |
| Early Hints (103) | ❌ | ✅ | ✅ | ✅ |
| Mirage (mobile img) | ❌ | ✅ | ✅ | ✅ |
| WAF Managed Rules | ❌ | ✅ | ✅ | ✅ |
| Image Resizing | ❌ | ❌ | ✅ | ✅ |
| Cache Key customization | ❌ | ❌ | ✅ | ✅ |
| Transform Rules | ✅ | ✅ | ✅ | ✅ |

## The Stack — What Each Piece Does

### 1. Cache Rules (replaces legacy "Cache Everything" Page Rule)

By default, Cloudflare caches static assets by file extension (.css, .js, .png). HTML and JSON are NOT cached. Cache Rules force Cloudflare to cache HTML responses.

**How to configure (Dashboard):**
- Rules > Cache Rules > Create Rule
- Expression: `(http.host eq "example.com")` or broader
- Settings:
  - **Cache eligibility**: "Eligible for cache"
  - **Edge TTL**: "Ignore cache-control header and use this TTL" → 3600s (1h) for dynamic pages, 86400s (24h) for static
  - **Browser TTL**: "Override origin" → 14400s (4h) to 86400s (24h)
  - **Serve Stale**: Enable — serve expired content while revalidating in background

**Via API:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cache HTML",
    "kind": "zone",
    "phase": "http_request_cache_settings",
    "rules": [{
      "expression": "(http.host eq \"example.com\")",
      "action": "cache",
      "action_parameters": {
        "edge_ttl": {"mode": "override_origin", "default": 3600},
        "browser_ttl": {"mode": "override_origin", "default": 14400},
        "serve_stale": {"disable_stale_while_updating": false}
      },
      "description": "Cache HTML with 1h edge TTL",
      "enabled": true
    }]
  }'
```

**Critical caveat:** Origin `Cache-Control: no-store` and `Set-Cookie` headers normally prevent caching. The Edge TTL override in Cache Rules forces caching regardless. Without this override, CF respects origin headers and won't cache.

### 2. Smart Tiered Cache (Pro+)

Divides CF datacenters into lower-tiers (edge, close to visitors) and upper-tiers (one per origin, selected dynamically by latency). Only the upper-tier can contact origin.

- Reduces origin load by limiting which DCs can fetch from origin
- Pro+ plan required
- Enable: Caching > Configuration > Tiered Cache > Smart Tiered Cache
- Does NOT eliminate origin requests — just reduces them

### 3. Cache Reserve (Pro+, usage-based)

The "ultimate upper-tier" — a persistent data store on R2 that acts as a cache layer behind all edge DCs.

- Assets must have TTL >= 10 hours to be eligible
- Retention: 30 days, resets on each request
- Pricing: $0.015/GB-month storage, $0.36/M reads, $4.50/M writes
- Enable: Caching > Configuration > Cache Reserve
- Designed to work WITH Tiered Cache for maximum origin shielding

### 4. Origin Headers

The origin must cooperate. Best practices:

```
Cache-Control: public, max-age=86400, s-maxage=86400
```
- `public` = cacheable by CDNs
- `max-age` = browser cache duration (seconds)
- `s-maxage` = shared cache (CDN) duration, overrides max-age for CF

For Next.js specifically:
```js
// next.config.js
module.exports = {
  async headers() {
    return [{
      source: '/(.*)',
      headers: [
        { key: 'Cache-Control', value: 'public, s-maxage=3600, stale-while-revalidate=86400' }
      ]
    }]
  }
}
```

### 5. Transform Rules (Free — critical for Next.js)

Transform Rules let you modify request/response headers at the CF edge. This is essential for fixing cache-busting patterns without changing origin code.

**Strip Vary headers (cache fragmentation killer):**
Next.js adds `vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch` which fragments the cache into separate variants. Most visitors don't send these headers, so each variant has near-zero hit rate.

Dashboard: Rules > Transform Rules > Modify Response Header
- Expression: `(http.host eq "example.com")`
- Operations: Remove `Vary`, then Add `Vary: Accept-Encoding`

**Strip Set-Cookie from cacheable pages:**
`Set-Cookie` on a response prevents CF from caching it by default. If you can't fix origin, use Transform Rules to remove the cookie from cacheable page responses.

Dashboard: Rules > Transform Rules > Modify Response Header
- Expression: `(http.host eq "example.com" and not http.request.uri.path contains "/api/")`
- Operations: Remove `Set-Cookie`

## Common Cache-Busting Patterns

| Pattern | Why it kills cache | Fix |
|---------|-------------------|-----|
| `Set-Cookie` on HTML | CF default: don't cache responses with cookies | Cache Rule Edge TTL override + Transform Rule to strip cookie |
| `Vary: rsc, next-router-state-tree, ...` (Next.js RSC) | Fragments cache by header value most visitors don't send | Transform Rule: remove Vary, re-add `Vary: Accept-Encoding` |
| `Cache-Control: no-store` | Explicit instruction to not cache | Cache Rule Edge TTL override (ignores origin) |
| `Vary: Cookie` | Fragments cache by cookie value | Transform Rule: remove Vary |
| Unique query strings (UTM, fbclid) | Creates separate cache entry per param | Cache Key standardization (Biz+) or strip params |
| Dynamic session IDs in URLs | Each URL is unique = 0% hit | Remove session IDs from URLs |
| Nonce in response body | Each response is unique | Not a caching issue (CF caches full response) |

## Audit Checklist

### A. Cache Rules & HTML Caching

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| A1 | Cache Rule for HTML exists | `curl -sI URL` → look for `cf-cache-status` | `HIT` or `REVALIDATED` on 2nd+ request | Create Cache Rule |
| A2 | Edge TTL override | Cache Rule settings | "Ignore cache-control" with 3600s+ TTL | Set in Cache Rule |
| A3 | Browser TTL override | Cache Rule settings | Override origin, 14400s+ | Set in Cache Rule |
| A4 | Serve Stale enabled | Cache Rule settings | Enabled | Enable in Cache Rule |
| A5 | Cache by query string | Caching > Configuration | `aggressive` (default on Free) | Set to aggressive |
| A6 | No Cache Rules exist | API: `/zones/$ZONE/rulesets` → phase `http_request_cache_settings` | At least 1 rule | Create one |

### B. Tiered Cache & Cache Reserve (Pro+)

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| B1 | Smart Tiered Cache | API: `/zones/$ZONE/settings/tiered_caching` | `enabled` | Enable (Pro+) |
| B2 | Cache Reserve | API: `/zones/$ZONE/settings/cache_reserve` | `enabled` | Enable (Pro+) |

### C. Performance Headers

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| C1 | `cf-cache-status` on HTML | `curl -sI URL \| grep cf-cache-status` | `HIT` on 2nd+ request | If missing = not cached, create Cache Rule |
| C2 | TTFB on cache HIT | `curl -w "%{time_starttransfer}" -o /dev/null -s URL` | < 50ms | If > 100ms, investigate |
| C3 | `cf-cache-status` on static | `curl -sI URL/sitemap.xml \| grep cf-cache-status` | `HIT` | Should be automatic |
| C4 | Cache hit ratio | CF Dashboard > Caching > Analytics | > 80% for content sites | Audit cache-busting patterns |

### D. Cache-Busting Detection

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| D1 | Set-Cookie on HTML | `curl -sI URL \| grep -i set-cookie` | None on cacheable pages | Transform Rule or origin fix |
| D2 | Vary header | `curl -sI URL \| grep -i vary` | `Accept-Encoding` only | Transform Rule to strip extra Vary |
| D3 | Cache-Control | `curl -sI URL \| grep -i cache-control` | `public, s-maxage=X` | Fix origin or Cache Rule override |
| D4 | UTM fragmentation | Check Cache Key config | Standardized or params stripped | Cache Key rule (Biz+) |

### E. Static Assets

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| E1 | Static assets cached | `curl -sI URL/favicon.ico \| grep cf-cache-status` | `HIT` | Ensure served as static, not catch-all |
| E2 | JS/CSS minification | Dashboard > Speed > Optimization > Auto Minify | JS + CSS ON | Enable (free) |
| E3 | Brotli | Dashboard > Speed > Optimization | ON | Enable (free) |
| E4 | Polish | Dashboard > Speed > Optimization | ON (Pro+) | Enable if Pro |

### F. DNS & SSL

| # | Parameter | How to check | Expected | Fix |
|---|-----------|-------------|----------|-----|
| F1 | Proxied (orange cloud) | DNS Records | All web records proxied | Enable proxy |
| F2 | SSL/TLS mode | SSL/TLS > Overview | Full (Strict) | Set to Full (Strict) |
| F3 | Always Use HTTPS | SSL/TLS > Edge Certificates | Enabled | Enable |
| F4 | HSTS | SSL/TLS > Edge Certificates | Enabled with preload | Enable |

## How to Run an Audit

### Step 1: Get zone ID

```bash
curl -s "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "Authorization: Bearer $CF_API_TOKEN" | python3 -c "
import json,sys; d=json.load(sys.stdin)
z=d['result'][0]; print(f'Zone: {z[\"name\"]} | ID: {z[\"id\"]} | Plan: {z[\"plan\"][\"name\"]}')"
```

### Step 2: Check all settings at once

```bash
# Get all zone settings
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings" \
  -H "Authorization: Bearer $CF_API_TOKEN" | python3 -c "
import json,sys
data=json.load(sys.stdin)
settings={s['id']:s['value'] for s in data['result']}
important=['browser_cache_ttl','cache_level','ssl','minify','brotli','polish',
           'early_hints','rocket_loader','tiered_caching','cache_reserve']
for k in important:
    if k in settings: print(f'  {k}: {settings[k]}')"
```

### Step 3: Check rulesets (Cache Rules, Transform Rules)

```bash
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets" \
  -H "Authorization: Bearer $CF_API_TOKEN" | python3 -c "
import json,sys
data=json.load(sys.stdin)
for rs in data.get('result',[]):
    p=rs.get('phase','?'); n=rs.get('name','?'); c=len(rs.get('rules',[]))
    print(f'  Phase: {p} | Name: {n} | Rules: {c}')"
```

### Step 4: Test response headers

```bash
# Check cache status + performance
curl -sI https://example.com/ | grep -iE '(cf-cache-status|cache-control|set-cookie|vary)'

# Measure TTFB (3 requests to see cache warm-up)
for i in 1 2 3; do
  curl -w "Req $i: ttfb=%{time_starttransfer}s total=%{time_total}s\n" \
    -o /dev/null -s https://example.com/
done

# Check cache HIT after warm-up
for i in 1 2 3; do
  echo -n "Req $i: "
  curl -sI https://example.com/ | grep -i cf-cache-status
done
```

### Step 5: Compile findings

For each checklist item, record:
- **Status**: ✅ OK / ⚠️ Suboptimal / ❌ Missing / ➖ N/A (plan limitation)
- **Current value**: What's configured now
- **Recommended value**: What it should be
- **Impact**: High / Medium / Low
- **Action**: Specific fix

### Step 6: Write report

Use the report structure from the audit output: Summary table (category, score), detailed findings per category with status/current/recommended, Quick Wins section (prioritized by impact), and Performance Impact Estimate table.

## Next.js-Specific Pitfalls

Next.js (especially App Router with RSC) has several patterns that destroy Cloudflare cache hit rates:

1. **`vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch`**
   - Added automatically by Next.js App Router
   - Fragments cache into variants most visitors never hit
   - Fix: Transform Rule to strip, re-add `Vary: Accept-Encoding`

2. **`set-cookie: NEXT_LOCALE=en`**
   - Set by Next.js i18n middleware on every response
   - Prevents CF caching by default
   - Fix: Transform Rule to strip, or middleware to only set on redirect

3. **Nonces in CSP**
   - Next.js generates unique nonce per request for script-src
   - Not a caching issue (CF caches full response including nonce)
   - But means cached pages have stale nonces for inline scripts — verify CSP still works

4. **Catch-all routes serving static files**
   - `favicon.ico`, `robots.txt` may be served by Next.js catch-all as HTML
   - Fix: Place actual static files in `public/` directory

5. **`cache-control: no-store` on API routes**
   - Correct behavior, but ensure Cache Rule expression excludes API routes if needed

## Cloudflare Pages / Workers Specifics

When origin is CF Pages (AAAA 100::) or Workers:
- SSL mode doesn't matter (internal CF connection) but set Full (Strict) anyway
- Origin response time is SSR computation, not network latency
- TTFB of 100-300ms is SSR time, not network — caching eliminates this entirely
- Cache Rules still apply the same way
- `s-maxage` in origin headers tells CF Pages to cache at the edge

## Sources

- [Default Cache Behavior](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/)
- [Cache Rules Settings](https://developers.cloudflare.com/cache/how-to/cache-rules/settings/)
- [Tiered Cache](https://developers.cloudflare.com/cache/about/tiered-cache/)
- [Cache Reserve](https://developers.cloudflare.com/cache/about/cache-reserve/)
- [Cache-Control Headers](https://developers.cloudflare.com/cache/concepts/cache-control/)
- [Transform Rules](https://developers.cloudflare.com/rules/transform/)
- [Cache Analytics](https://developers.cloudflare.com/cache/about/cache-analytics/)
