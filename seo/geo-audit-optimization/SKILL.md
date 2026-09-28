---
name: geo-audit-optimization
description: >
  Audit and optimize a website's Generative Engine Optimization (GEO) presence.
  Trigger when user asks about AI visibility, ChatGPT/Perplexity citations, LLM rankings,
  GEO audit, AI search optimization, brand mentions in AI, or "appear in ChatGPT".
  Covers fan-out query analysis, language arbitrage, parasite GEO, source identification,
  and link budget redesign for AI-era search.
---

# GEO Audit & Optimization Skill

Audit and optimize a website's visibility in AI-powered search engines (ChatGPT, Perplexity, Copilot, Gemini, Claude).

## Core Principle

**GEO is 90% reputation/media, 10% technical.** The goal is to be cited in sources that LLMs retrieve and trust when they perform their "fan-out" searches.

---

## Phase 1: GEO Baseline Audit

### 1.1 Brand Citation Check

Test the brand across all major LLMs. For each, record:

```bash
# For each LLM, ask these queries and log the responses:
# - "What is [brand]?"
# - "Best [product category] in [country]"
# - "Top [service] providers 2026"
# - "[brand] reviews"
# - "Is [brand] legit?"
```

**LLMs to test:**
- ChatGPT (free + Plus with browsing)
- Perplexity (free + Pro)
- Microsoft Copilot (Bing integration)
- Google Gemini
- Claude (with web search)
- You.com

**Record per query:**
- Is the brand mentioned? (Yes/No)
- Position (1st, 2nd, 3rd, mentioned but late, not mentioned)
- Sources cited by the LLM (URLs)
- Sentiment (positive, neutral, negative)
- Accuracy of information

### 1.2 Fan-Out Query Analysis

When ChatGPT answers a query, it makes **multiple sub-queries** internally. To reverse-engineer these:

1. **Use ChatGPT Plus with browsing** and ask your target query
2. **Click "Sources"** to see which URLs it retrieved
3. **Analyze the diversity** of sources — are they blogs, forums, directories, media?
4. **Note the language** — ChatGPT often rewrites queries in English even for French requests
5. **Record the exact sub-queries** when visible (some tools like Perplexity show them)

**Key insight:** ChatGPT often transforms a simple French query like "meilleur site CBD France" into multiple English sub-queries like:
- "top CBD sites in France reviews 2026"
- "best French CBD shops customer ratings"
- "CBD France legal quality comparison"

This creates **language arbitrage opportunities** (see Phase 2).

### 1.3 Source Ecosystem Mapping

For your target keywords, identify:

| Source Type | Examples | Weight in GEO |
|-------------|----------|---------------|
| Media rankings | Le Point, Le Monde rankings | Very High |
| Independent review sites | Affiliate sites, comparison blogs | High |
| Reddit / Quora / Forums | UGC discussions | High |
| Brand own content | Website, blog | Medium |
| Social proof | TikTok, YouTube mentions | Medium-High |
| Technical docs | Schema, llms.txt | Low (5-10%) |
| Directory listings | GMB, Yelp, industry dirs | Medium |

---

## Phase 2: GEO Optimization Strategies

### 2.1 Link Budget Redesign

**Old model:** Buy backlinks for traditional SEO juice.
**New model:** 90% of backlink budget → content on rankable, GEO-friendly sites.

```yaml
# Link budget allocation for GEO:
geo_friendly_content: 90%   # Content on sites that rank in Google/ChatGPT
traditional_backlinks: 10%  # Classic SEO link building

# What "GEO-friendly content" means:
# - "Top 10 best [category]" articles on authority sites
# - Comparative reviews that LLMs will cite
# - Placement on sites that already appear in ChatGPT sources
# - Budget range: 50-300 EUR per placement
```

**Execution:**
1. Identify sites that ChatGPT already cites for your keywords
2. Negotiate content placement on those exact sites
3. Write content that naturally includes/recommends the brand
4. Ensure the content targets the exact fan-out sub-queries

### 2.2 Language Arbitrage

**Discovery:** ChatGPT often searches in English even when the user query is in French.

**Method:**
1. Ask ChatGPT a French query about your niche
2. Check what language the source queries were in
3. If English → create English content about your French topic
4. Competition is 100x lower for "best [category] France" in English vs French

**Example:**
- Query: "Quel est le meilleur site de CBD en France ?"
- ChatGPT internal search: "top CBD sites in France reviews"
- Action: Write English reviews of French CBD sites on English-language platforms

### 2.3 Parasite SEO for GEO

Place content on high-authority domains that LLMs trust:

1. **Identify parasite targets:** Sites with high domain authority that accept guest content
2. **Create GEO-optimized content:** Target the exact fan-out queries
3. **Include brand mentions:** Natural recommendations, comparisons, "best of" lists
4. **Cross-reference:** Get multiple parasite articles to cite each other

**Best parasite targets for GEO:**
- Medium, LinkedIn articles (high trust)
- Industry-specific platforms
- News sites with contributor programs
- Expired domains with existing authority (use cautiously)

### 2.4 Source Identification & Interception

```python
# Workflow to identify and intercept GEO sources:

# 1. Query ChatGPT for your target keywords
# 2. Extract all cited URLs
# 3. Categorize each source:
for source in cited_urls:
    source_type = classify(source)  # media, affiliate, forum, directory
    authority = check_da(source)
    can_place = check_contributor_option(source)
    
# 4. For sources you CAN'T place on:
#    → Get cited BY them (PR, outreach, partnerships)
# 5. For sources you CAN place on:
#    → Place content directly
# 6. For gaps (no source exists):
#    → Create the source yourself on a parasite domain
```

### 2.5 GPT Quote as Sales Lever

For agencies/consultants selling GEO services:

1. Query ChatGPT for the client's niche
2. Show the client their current citation status
3. Show the **exact source** ChatGPT trusts
4. Explain: "If I change this source, ChatGPT's answer changes"
5. This creates urgency and justifies GEO pricing

### 2.6 Affiliate + GEO Synergy

Affiliate programs naturally generate GEO signals:
- Affiliates create content mentioning the brand on multiple platforms
- YouTube videos, blog posts, reviews = brand signals for LLMs
- More mentions = higher chance of being cited in AI search

**Action:** Launch or expand affiliate programs as a GEO strategy, not just a sales channel.

---

## Phase 3: Technical GEO (5-10% of impact)

While technical GEO is a small fraction of total impact, it should be implemented:

### 3.1 Structured Data
- JSON-LD on all key pages
- FAQ schema for common questions
- Product/Review schema for e-commerce
- Organization schema with sameAs links

### 3.2 llms.txt
- Create `/llms.txt` file (emerging standard)
- List key pages, brand description, contact info
- Keep it updated

### 3.3 Content Structure
- Clear H1/H2 hierarchy
- Direct answers to common questions
- Factual, verifiable claims with sources
- Avoid marketing fluff — LLMs prefer factual content

### 3.4 Crawlability
- Ensure AI crawlers can access content (don't block GPTBot, etc.)
- Submit to Bing Webmaster Tools (powers Copilot)
- Monitor Bing Webmaster "citations" data

---

## Phase 4: KPI / Metrics Checklist

### GEO Visibility Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **GEO Citation Share** | >30% of target queries | Manual LLM testing across 5+ platforms |
| **Brand Mention Rate** | >80% for brand queries | Test "[brand]" across all LLMs |
| **Source Position** | Top 3 cited sources | Record position in each LLM response |
| **Citation Accuracy** | >95% correct info | Verify facts in LLM responses |
| **Sentiment Score** | >80% positive | Classify LLM response sentiment |
| **Fan-Out Coverage** | >50% of sub-queries | Map and track sub-query appearances |
| **Language Arbitrage Wins** | Track EN content ranking for FR queries | Monitor cross-language citations |

### Traffic & Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **LLM Referral Traffic** | Growing month-over-month | GA4: filter by chatgpt.com, perplexity.ai, copilot.microsoft.com referrers |
| **GEO-Driven Leads** | Track conversion rate | UTM-tagged links in GEO content |
| **GEO vs SEO Traffic Ratio** | Monitor trend | Compare LLM referral vs organic search |
| **Citation Longevity** | Citations persist >30 days | Re-test monthly |
| **Competitor GEO Gap** | More citations than competitors | Side-by-side LLM testing |

### Link & Content Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **GEO-Friendly Link %** | >90% of new links | Classify each new link by GEO relevance |
| **Parasite Content Rank** | Top 10 in Google for target queries | Track parasite page rankings |
| **Source Interception Rate** | >30% of ChatGPT sources | Compare before/after source lists |
| **Content Language Mix** | EN content for FR niches where applicable | Track multilingual content deployment |
| **Bing Citation Count** | Growing | Bing Webmaster Tools |

### Monthly GEO Audit Template

```markdown
## GEO Audit Report — [Month Year]

### Brand Queries Tested: [X]
- ChatGPT: [X/Y] mentions, avg position [N]
- Perplexity: [X/Y] mentions, avg position [N]
- Copilot: [X/Y] mentions, avg position [N]
- Gemini: [X/Y] mentions, avg position [N]

### Fan-Out Analysis
- Sub-queries mapped: [N]
- Coverage rate: [X%]
- New language arbitrage opportunities: [list]

### Actions Taken
- GEO-friendly placements: [N] new articles
- Sources intercepted: [list]
- Technical GEO updates: [list]

### Results
- LLM referral traffic: [N] visits (+X% MoM)
- GEO-driven leads: [N]
- New citations discovered: [list]

### Next Month Priorities
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

---

## Quick GEO Diagnosis

Run this checklist on any website to assess GEO readiness:

- [ ] Brand appears in ChatGPT when queried directly
- [ ] Brand appears in ChatGPT for category queries ("best [X]")
- [ ] Brand appears in Perplexity for category queries
- [ ] At least 3 independent sources cited by LLMs mention the brand
- [ ] English content exists about the brand (for language arbitrage)
- [ ] Affiliate/referral program generates organic mentions
- [ ] Structured data (JSON-LD) on key pages
- [ ] No AI crawlers blocked in robots.txt
- [ ] Bing Webmaster Tools configured
- [ ] Monthly LLM citation monitoring in place
- [ ] Link budget allocated to GEO-friendly placements
- [ ] Content targets fan-out sub-queries, not just primary keywords

**Scoring:**
- 10-12 checked: GEO-optimized
- 7-9 checked: Good foundation, optimize gaps
- 4-6 checked: Needs significant GEO work
- 0-3 checked: GEO blind spot — urgent action needed

