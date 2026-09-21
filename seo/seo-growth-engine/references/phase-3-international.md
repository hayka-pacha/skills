# Phase 3 — International SEO

## 3.1 Hreflang

```html
<!-- On EVERY page in the cluster -->
<link rel="alternate" hreflang="en" href="https://example.com/page" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page" />
<link rel="alternate" hreflang="es" href="https://example.com/es/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

**Critical rules:**
1. **Return links are mandatory.** If EN points to FR, FR must point back to EN. Missing return links is the #1 hreflang error — Google silently ignores orphaned hreflang.
2. **Self-referencing required.** The EN page must list itself as `hreflang="en"`.
3. **x-default** = fallback for unmatched locales (usually your primary version).
4. **Canonical and hreflang must agree.** A page's canonical should point to itself (or its hreflang twin, never to a different language).
5. **XML sitemap method scales better** than `<link>` tags once you have > 100 pages — implement hreflang in the sitemap's `<xhtml:link>` entries.
6. **Use language-region codes correctly**: `en-US`, `en-GB`, `pt-BR`, `pt-PT`. ISO 639-1 language + ISO 3166-1 alpha-2 region.

Common failure mode: code generates hreflang only for the "current" page's locale, missing self-reference and missing siblings. Build the cluster, render the full set on every page.

## 3.2 Locale Strategy

| Approach | Pros | Cons |
|----------|------|------|
| **Subdirectories** `/fr/` | Consolidates domain authority, one site to maintain | Shared IP geo-signals |
| Subdomains `fr.example.com` | Separate crawl budgets, can host on regional infra | Splits authority across hostnames |
| ccTLDs `.fr` | Strongest geo signal | Expensive, splits authority across domains, more ops |

**Default recommendation: subdirectories.** Confirmed best for most sites by Google, Ahrefs, Moz. Only choose ccTLDs when you have local teams, local infra, and budget — and traffic to justify the authority split.

## 3.3 Localization ≠ Translation

Direct translation loses 30-50% of potential traffic vs proper localization (SEMrush study).

- **Research local keywords**. "Trainers" (UK) vs "sneakers" (US). "Voiture d'occasion" vs "voiture seconde main". Locals don't search the way translators translate.
- **Adapt examples, currency, units, holidays, cultural references**.
- **Local internal linking patterns**. Link to local resources, not US-centric ones.
- **Localized structured data**: prices in local currency, availability for local market.
- **Local backlinks** matter more than total backlinks for geo-ranking.

## Sources

Google hreflang docs, Ahrefs International SEO, SEMrush Localization research. Full list in `sources.md`.
