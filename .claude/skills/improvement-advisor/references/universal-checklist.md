# Universal GEO Optimization Dimensions

When generating site-wide improvement suggestions, evaluate each dimension below. Skip dimensions that have no supporting evidence from the diagnostic data.

## 1. PAGE_STRUCTURE
- Page titles include product name + core topic
- H1 tags are descriptive and unique per page
- First paragraph contains a complete, self-contained answer (answer-first principle)
- Content is chunking-friendly: H2/H3 sections are self-contained, tables preferred over long paragraphs
- No multi-topic pages (one page = one knowledge unit)

## 2. SCHEMA_MARKUP
- FAQPage schema on FAQ pages
- HowTo schema on tutorial/guide pages
- TechArticle schema on API documentation
- SoftwareApplication schema on product/version pages
- Article schema with datePublished on blog posts
- Event schema on community event pages

## 3. DISAMBIGUATION
- Terms with cross-product ambiguity include product name in first mention
- Page title includes product context, not just term name
- First paragraph contains explicit disambiguation ("X in MindSpore, not to be confused with Y")
- Meta keywords include product + term + domain combinations
- Glossary page exists with canonical definitions

## 4. NEGATION_CONVENTION
- Limitations/unsupported features stated in the first sentence
- Negation before alternatives ("does not support X. Alternative: Y")
- Unsupported items listed individually, not as "etc."
- Schema Answer.text leads with negation for limitation-type questions
- Bold/highlight formatting on negative statements

## 5. VERSION_SEO
- Canonical tags on all versioned pages pointing to /stable/
- noindex on EOL versions
- Version freshness banner on non-latest pages
- hreflang tags for multi-language pages
- Sitemap.xml contains only stable version URLs
- Stable URL (/stable/) always redirects to latest version

## 6. CONTENT_LAYERING
Content should be organized in 4 tiers by AI citation frequency:
- Tier 1 (Core Concepts): Installation, key concepts, product positioning — answer-first, Schema-heavy
- Tier 2 (Tutorials): Step-by-step guides — HowTo Schema, numbered steps, code examples
- Tier 3 (Reference): API docs, operator lists, FAQ — complete parameters, exceptions, examples
- Tier 4 (Community): Blog, events, contributions — datePublished, Event Schema

## 7. EXTERNAL_PRESENCE
- GitHub README contains accurate core concept descriptions
- StackOverflow tag exists with seed answers
- CSDN/知乎/华为云博客content is factually consistent with official docs
- Incorrect third-party content is countered with official blog posts
- Key pages have inbound links from high-authority external sources

## 8. CRAWL_ACCESS
- robots.txt does not block AI platform crawlers (GPTBot, PerplexityBot, ClaudeBot, etc.)
- sitemap.xml is complete, up-to-date, with correct lastmod dates
- Core documentation pages load within 2.5s (LCP)
- Internal link structure ensures all pages are reachable within 3 clicks from homepage
- No orphan pages (pages with zero internal links pointing to them)

## 9. MONITORING
- Monthly GEO audit process defined (select questions, sample platforms, score, fix)
- Trigger-based audit on new version releases and FAQ additions
- KPI tracking: official citation rate, factual accuracy rate, negation transmission rate, context correctness rate, version freshness rate
- Feedback loop: community-reported AI errors flow into improvement pipeline
