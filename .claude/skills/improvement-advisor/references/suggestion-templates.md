# Per-Question Suggestion Categories

Each suggestion targets a specific page or content section on the official website.

## Category Definitions

### content_fix
Direct content correction or enhancement on a specific page.
- Fixing factually incorrect statements
- Adding missing information
- Correcting code examples or API references

### schema_markup
Adding or improving structured data markup (Schema.org JSON-LD).
- FAQPage for FAQ pages
- HowTo for tutorial pages
- TechArticle for API documentation
- SoftwareApplication for product pages

### title_disambiguation
Improving page titles, H1 tags, and meta descriptions to prevent AI platforms from confusing the content with other products or concepts.
- Adding product name prefix (e.g., "MindSpore TransData" not just "TransData")
- Adding domain context (e.g., "tensor format conversion" not just "data conversion")
- Explicit disambiguation statements in first paragraph

### negation_reinforcement
Strengthening expressions of limitations, unsupported features, or boundaries.
- Moving negation to the first sentence
- Using bold/highlight for "does not support" statements
- Including explicit negative keywords that users might search for
- Listing unsupported items individually, not as "etc."

### version_seo
Improving version-specific SEO to prevent AI platforms from citing outdated documentation.
- Adding canonical tags to point to stable version
- Adding noindex to deprecated versions
- Adding version freshness banners

### keyword_coverage
Expanding keyword coverage so AI platforms can find the content when users phrase questions differently.
- Adding alternative phrasings (e.g., "load PyTorch model" alongside "read other framework models")
- Including competitor terminology where relevant (e.g., "like PyTorch's torch.load()")
- Covering common misspellings or abbreviations

## Suggestion JSON Schema

```json
{
  "category": "content_fix|schema_markup|title_disambiguation|negation_reinforcement|version_seo|keyword_coverage",
  "target": "URL or page identifier",
  "current_state": "what the page currently says/does",
  "recommended_change": "exact change to make",
  "priority": "P0|P1|P2",
  "rationale": "why this change improves AI platform responses",
  "expected_impact": "which platforms benefit and how"
}
```

## Priority Definitions

- **P0 (Critical):** Factual errors appear in multiple AI platforms. Users are being actively misled. Fix within 1-2 weeks.
- **P1 (High):** Single-platform errors, citation gaps, or missing information that degrades response quality. Fix within 2-4 weeks.
- **P2 (Medium):** Optimization opportunities that improve response quality but do not fix errors. Address within 1-2 months.
