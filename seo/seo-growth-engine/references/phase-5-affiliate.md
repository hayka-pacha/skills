# Phase 5 — Affiliate & Monetization SEO

## 5.1 Affiliate Link Hygiene

```html
<!-- CORRECT -->
<a href="https://affiliate.example/deal"
   rel="noopener noreferrer sponsored nofollow"
   target="_blank">View offer →</a>
```

Why it matters:
- `rel="sponsored"` tells Google this is a paid/commercial link. Required by Google's link spam policy.
- `rel="nofollow"` is belt-and-suspenders backwards compatibility.
- Missing these tags on heavy affiliate sites can trigger link spam penalties.

Other rules:
- **Never put affiliate URLs in schema.org markup** (e.g., `Product.url` or `Offer.url`). Schema should point to the canonical merchant page, not your tracking link. Mixing these is a deceptive markup violation.
- **Affiliate disclosure** clearly visible on every page with affiliate links (FTC requirement in the US, plus user trust).
- **`/go/` redirect paths** for outbound affiliate links: use **302** (temporary) — not 301. Block `/go/` in robots.txt so they don't get indexed.
- Don't cloak: serve the same destination to Googlebot and users.

## 5.2 Adding Real Value as an Affiliate

Google explicitly states thin affiliate pages that pass through to merchants provide poor UX. You earn rankings by being **better than the merchant page** for the user's query.

Value-add patterns that work:
1. **Aggregated data** — availability, pricing history, ratings, specs combined from multiple sources.
2. **Comparisons** — side-by-side products/services with real differentiators highlighted.
3. **Editorial content** — genuine reviews with pros/cons, recommendations, use cases.
4. **User-generated signals** — ratings, favorites, comments, Q&A.
5. **Unique tools** — search, filtering, calculators, sizing guides not available on source sites.
6. **First-hand experience** — photos you took, tests you ran. Strong E-E-A-T signal.

The test: if a user is on your affiliate page and another tab has the merchant's page, which gives them more useful information? If the merchant wins, you're thin content.

## 5.3 Audience-Restricted Content & SafeSearch

When a site mixes general-audience editorial with sections meant for restricted audiences (adult content, age-gated material), follow [Google's explicit content guidelines](https://developers.google.com/search/docs/specialty/explicit/guidelines):

- **Restricted-audience sections**: use the markup and meta values Google documents for your content type (e.g., `rating` meta where applicable). Don't hide it — explicit classification helps Google rank you correctly in the right context.
- **Broad-reach editorial** (reviews, guides, news): keep these on a clearly separate URL pattern, indexed normally for general discovery.
- **Split intent clearly**: restricted catalog/listings vs general informational content, each optimized for the right queries and SafeSearch filters.

The goal is *correct* classification, not avoidance. Mis-classified content gets filtered out or surfaces in wrong contexts — both lose traffic.

## Sources

Google Link Spam docs, Google Affiliate Programs guide, Google Explicit Content/SafeSearch guidelines. Full list in `sources.md`.
