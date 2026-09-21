# Phase 2 — Content & On-Page SEO

## 2.1 E-E-A-T

Google's quality framework (Search Quality Evaluator Guidelines):
- **Experience** — show first-hand experience with the topic (photos you took, tests you ran, things you used)
- **Expertise** — depth of knowledge
- **Authoritativeness** — reputation: backlinks, mentions, reviews
- **Trustworthiness** — HTTPS, transparent affiliate disclosure, privacy policy, accurate info

For affiliate sites specifically, Google's affiliate guidelines require **original value** beyond merchant-supplied data:
- Proprietary comparisons, user ratings, schedules, availability data
- Genuine editorial opinion — not regurgitated product descriptions
- Clear affiliate disclosure on every page with affiliate links
- Minimum **500 words of unique content** per programmatic page

## 2.2 Heading Hierarchy

```html
<h1>One per page — primary keyword</h1>
  <h2>Section — secondary keyword</h2>
    <h3>Subsection — long-tail variant</h3>
  <h2>Another section</h2>
```

Rules: single H1. Logical nesting. Don't skip levels (h1 → h3). Headings should describe sections accurately, not be a keyword graveyard.

## 2.3 Internal Linking

The most underrated SEO lever. Google uses internal links to discover pages, distribute PageRank, and understand topical relationships.

- **3-10 internal links per page** to related content
- **Descriptive anchor text** (not "click here") — but vary it; exact-match anchors everywhere looks manipulated
- Link from high-authority pages to new or important pages to pass authority
- Build **topic clusters**: pillar page links to supporting pages, supporting pages link back
- Product/listing detail: link to related items + same brand + same category + relevant blog posts
- Blog post: link to related posts + relevant product/listing pages + category pages
- Footer: top categories + top blog posts + brand or merchant guides

**Crawlable text links beat JavaScript navigation.** Googlebot can execute JS but text links are cheaper and more reliable.

## 2.4 Image SEO

Checklist:
- Descriptive alt text on every meaningful image (decorative = `alt=""`)
- Descriptive filenames (`trail-jacket-navy.webp`, not `IMG_1234.jpg`)
- WebP/AVIF format (30-50% smaller than JPEG at equivalent quality)
- Responsive `srcset`/`sizes`
- Lazy-load below-fold images
- `priority` / `fetchPriority="high"` on **only the LCP image** — more dilutes priority
- Include images in an image sitemap for Google Images traffic

Image search drives meaningful traffic for visual niches (recipes, fashion, products). Don't ignore it.

## Sources

Google Search Quality Evaluator Guidelines, Ahrefs On-Page guide, SEJ Internal Linking, Google Image Best Practices. Full list in `sources.md`.
