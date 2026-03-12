---
name: improvement-advisor
description: Analyzes AI platform responses against official standard answers and generates actionable GEO (Generative Engine Optimization) improvement suggestions. Reads responses.json (from platform-sampler) and official answers, then scores each response on citation accuracy, factual correctness, and context matching. Outputs a structured improvement report covering per-question diagnostics (hallucination, context mismatch, intent drift) and site-wide universal recommendations (Schema markup, keyword disambiguation, negation expression, version SEO, content discoverability). Produces improvement-report.json and improvement-report.md with prioritized action items. Use when platform responses have been collected and need diagnosis. Do not use for question generation, platform sampling, or response scoring without standard answers.
---

# Improvement Advisor

Analyze AI platform responses against official standard answers and generate prioritized GEO improvement suggestions — both per-question diagnostics and site-wide universal recommendations.

## Prerequisites

- `responses.json` in the project root (output from platform-sampler skill)
- Official standard answers available in one of:
  - `standard-answers.json` (structured format, preferred)
  - `INPUT.md` or answer files in `Answers/` directory (Markdown format)
- Recognized citation sources configured (defaults to community's official website and repositories)

## Procedures

**Step 1: Load and Validate Inputs**

1. Read `responses.json` from the project root.
2. Run `python3 scripts/validate-input.py responses.json` to verify structure.
3. If validation fails, display the error and abort.
4. Load official standard answers:
   - If `standard-answers.json` exists, read it directly.
   - Otherwise, scan `INPUT.md` and `Answers/*.md` for question-answer pairs. Extract the official answer text and source URLs for each question.
5. Load recognized citation sources from `.env` field `OFFICIAL_DOMAINS` (comma-separated). Default: `mindspore.cn,gitee.com/mindspore,github.com/mindspore-ai`.
6. Print loaded question count, platform count, and standard answer count to stdout.

**Step 2: Per-Question Diagnosis**

For each question that has both platform responses and a standard answer:

1. Extract the standard answer's key facts as a checklist. Prompt the LLM:
   ```
   Given the following official standard answer:

   {standard_answer}

   Extract a list of key facts (atomic claims) that a correct response MUST convey.
   Mark each fact as either:
   - POSITIVE (something that IS true, e.g., "supports Ascend/GPU/CPU")
   - NEGATIVE (something that is NOT true / a limitation, e.g., "cannot directly read PyTorch models")

   Output as JSON array: [{"fact": "...", "polarity": "POSITIVE|NEGATIVE"}]
   ```

2. For each platform response, run the diagnostic prompt:
   ```
   You are a GEO diagnostic engine. Compare this AI platform response against the official key facts.

   Question: {question}
   Platform: {platform_name}
   Platform Response: {response_text}
   Official Key Facts: {key_facts_json}
   Recognized Citation Sources: {official_domains}

   Evaluate and output JSON:
   {
     "question_id": "...",
     "platform": "...",
     "citation_analysis": {
       "total_citations": <int>,
       "official_citations": <int>,  // URLs matching recognized sources
       "unofficial_citations": <int>,
       "fabricated_citations": <int>,  // URLs that appear invalid or non-existent
       "cited_urls": ["..."]
     },
     "fact_coverage": {
       "covered_facts": ["..."],  // key facts correctly conveyed
       "missed_facts": ["..."],   // key facts omitted
       "contradicted_facts": ["..."],  // key facts stated incorrectly (opposite)
       "fabricated_claims": ["..."]  // claims not in standard answer and likely false
     },
     "failure_mode": "none|hallucination|context_mismatch|intent_drift|partial_error",
     "failure_detail": "...",  // human-readable explanation if failure_mode != none
     "negation_handling": "correct|missed|reversed",  // for NEGATIVE polarity facts
     "severity": "none|low|medium|high|critical",
     "accuracy_score": <0-5>  // 0=completely wrong, 5=perfect match
   }
   ```

3. Collect all diagnostic results into `diagnostics[]`.

**Step 3: Cross-Platform Pattern Analysis**

1. Group diagnostics by question. For each question, identify:
   - Which platforms got it right vs wrong
   - Common failure modes across platforms
   - Whether the failure is platform-specific or content-origin (affects multiple platforms)

2. Group diagnostics by failure mode. Prompt the LLM:
   ```
   Given the following diagnostic results across all questions and platforms:

   {diagnostics_json}

   Identify recurring patterns:
   1. HALLUCINATION patterns: Which topics/terms trigger fabricated claims? On which platforms?
   2. CONTEXT_MISMATCH patterns: Which terms are ambiguous? What are they confused with?
   3. INTENT_DRIFT patterns: Which questions cause off-topic responses? On which platforms?
   4. NEGATION failures: Which negative facts are consistently missed or reversed?
   5. CITATION gaps: Which pages/topics have zero official citations across all platforms?

   Output as JSON:
   {
     "hallucination_patterns": [{"trigger": "...", "platforms": [...], "example": "..."}],
     "context_mismatch_patterns": [{"term": "...", "confused_with": "...", "platforms": [...]}],
     "intent_drift_patterns": [{"question": "...", "drift_target": "...", "platforms": [...]}],
     "negation_failures": [{"fact": "...", "platforms_missed": [...]}],
     "citation_gaps": [{"topic": "...", "suggested_page": "..."}]
   }
   ```

3. Store the pattern analysis result.

**Step 4: Generate Per-Question Improvement Suggestions**

For each question with identified issues, generate targeted improvements:

1. Read `references/suggestion-templates.md` for the suggestion format and category definitions.

2. Prompt the LLM:
   ```
   Based on the diagnostic for question "{question}":

   Diagnostic: {diagnostic_json}
   Pattern context: {pattern_analysis_json}

   Generate specific, actionable improvement suggestions. Each suggestion must include:
   - category: one of "content_fix", "schema_markup", "title_disambiguation", "negation_reinforcement", "version_seo", "keyword_coverage"
   - target: which page/section on the official site to modify
   - current_state: what the page currently says/does
   - recommended_change: exact change to make
   - priority: "P0" (critical, factual error in multiple platforms), "P1" (high, single platform error or citation gap), "P2" (medium, optimization opportunity)
   - rationale: why this change will improve AI platform responses
   - expected_impact: which platforms will benefit and how

   Output as JSON array of suggestions.
   ```

3. Collect all per-question suggestions.

**Step 5: Generate Universal (Site-Wide) Improvement Suggestions**

1. Read `references/universal-checklist.md` for the full list of universal GEO optimization dimensions.

2. Based on the pattern analysis from Step 3 and per-question findings from Step 4, prompt the LLM:
   ```
   Based on the following cross-platform pattern analysis and per-question diagnostics:

   Patterns: {pattern_analysis_json}
   Per-question suggestions: {question_suggestions_json}
   Total questions analyzed: {count}
   Platforms: {platform_list}

   Generate universal (site-wide) improvement suggestions that address systemic issues,
   not just individual questions. Cover these dimensions (skip any that have no evidence):

   1. PAGE_STRUCTURE: Page title, H1, first-paragraph, chunking friendliness
   2. SCHEMA_MARKUP: Structured data (FAQPage, HowTo, TechArticle, etc.)
   3. DISAMBIGUATION: Terms that need product-context clarification
   4. NEGATION_CONVENTION: Site-wide rules for expressing limitations/unsupported features
   5. VERSION_SEO: Canonical tags, noindex for old versions, stable URL routing
   6. CONTENT_LAYERING: Which content tiers (concepts/tutorials/API/community) need investment
   7. EXTERNAL_PRESENCE: GitHub README, StackOverflow, CSDN, knowledge base submissions
   8. CRAWL_ACCESS: robots.txt, sitemap.xml, page load performance for AI bots
   9. MONITORING: Ongoing audit processes and KPIs

   Each suggestion must include:
   - dimension: one of the above
   - title: short descriptive title
   - description: detailed actionable guidance
   - priority: P0/P1/P2
   - scope: "all_pages" / "faq_pages" / "api_docs" / "tutorials" / specific page types
   - evidence: reference to specific diagnostic findings that justify this suggestion

   Output as JSON array.
   ```

3. Collect universal suggestions.

**Step 6: Compile and Output**

1. Run `python3 scripts/compile-report.py` with the following inputs piped as JSON to stdin:
   ```json
   {
     "diagnostics": [...],
     "patterns": {...},
     "question_suggestions": [...],
     "universal_suggestions": [...],
     "metadata": {
       "date": "YYYY-MM-DD",
       "platforms": [...],
       "question_count": N,
       "official_domains": [...]
     }
   }
   ```
   The script:
   - Deduplicates suggestions with >80% text similarity
   - Sorts by priority (P0 → P1 → P2), then by impact breadth
   - Assigns unique IDs to each suggestion
   - Outputs `improvement-report.json` to stdout

2. Write the compiled JSON to `improvement-report.json` in the project root.

3. Generate `improvement-report.md` using the template in `assets/report-template.md`:
   - **Section 1: Executive Summary** — platform count, question count, overall accuracy distribution, top 3 failure patterns
   - **Section 2: Per-Question Analysis** — for each question: platform comparison table, key findings, specific suggestions
   - **Section 3: Universal Recommendations** — grouped by dimension, with priority tags
   - **Section 4: Execution Roadmap** — Phase 1 (P0, 1-2 weeks), Phase 2 (P1, 2-4 weeks), Phase 3 (P2, ongoing)
   - **Section 5: KPI Tracking** — suggested metrics and target values
   - **Appendix** — data source files, evaluation criteria

4. Write the Markdown report to `improvement-report.md` in the project root.

5. Print a summary to stdout:
   ```
   Improvement report generated:
     Questions analyzed: {N}
     Platforms: {platform_list}
     Per-question suggestions: {N_specific} (P0: {n}, P1: {n}, P2: {n})
     Universal suggestions: {N_universal} (P0: {n}, P1: {n}, P2: {n})
     Failure modes found: {mode_list}
     Output: improvement-report.json, improvement-report.md
   ```

**Step 7: Human Review Checkpoint**

1. Present the report summary to the user.
2. Highlight P0 items that require immediate attention.
3. Wait for user feedback before proceeding to any automated actions.
4. If the user provides corrections or overrides:
   - Apply the changes to the report
   - Save feedback to `feedback-rules.md` for future runs (learning loop)

## Error Handling

* If `responses.json` is missing, abort with: "responses.json not found. Run platform-sampler skill first."
* If no standard answers are found (neither `standard-answers.json` nor `INPUT.md` / `Answers/`), abort with: "No standard answers found. Provide standard-answers.json or populate Answers/ directory."
* If a question in `responses.json` has no matching standard answer, skip it with a warning: "No standard answer for question {id}, skipping diagnosis."
* If the LLM diagnostic prompt returns malformed JSON, retry once with a stricter format instruction. If still malformed, log the error and continue with remaining questions.
* If `scripts/compile-report.py` fails, display stderr and suggest manually reviewing the raw diagnostics output.
* If fewer than 3 questions have standard answers, warn: "Limited standard answer coverage ({N}/{total}). Report may not capture systemic patterns."
