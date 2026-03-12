---
name: scoring-engine
description: Evaluates AI platform responses using a two-layer model (content completeness + citation accuracy). Reads responses.json and content-labels.json, classifies each question-platform pair into phenomena (A-E), calculates official source citation ratios, assigns severity (P0-P2), and outputs scoring-results.json with suggestions.md. Supports human spot-check calibration via scoring-calibration.md feedback loop. Use after platform-sampler completes sampling. Do not use for question generation, platform sampling, or issue creation.
---

# Scoring Engine

Evaluate AI platform responses against official content availability. Two-layer assessment: content completeness (human-labeled) then citation accuracy (LLM-judged).

## Prerequisites

- `responses.json` in the project root (output from platform-sampler skill)
- `content-labels.json` in the project root (human pre-labeled: `content_exists`, `official_urls`, `content_coverage` per question)
- Optional: `scoring-calibration.md` (feedback from prior human spot-checks, incorporated as prompt context)

## Procedures

**Step 1: Load and Validate Inputs**

1. Read `responses.json` from the project root.
2. Run `python3 scripts/validate-inputs.py responses.json content-labels.json` to verify both files exist and are structurally valid.
3. The script checks:
   - `responses.json` contains a `responses` array with `question_id`, `platform`, `response_text` fields.
   - `content-labels.json` contains a `labels` array with `question_id`, `content_exists` fields.
   - Every `question_id` in responses has a matching label entry.
4. If validation fails, abort with the specific error from stderr.
5. If `scoring-calibration.md` exists, read it. This contains human corrections from prior rounds — use as additional prompt context in Step 3.

**Step 2: Layer 1 — Content Completeness**

1. Read `content-labels.json` and extract each question's `content_exists` value.
2. For each question where `content_exists` is `false` or `"none"`:
   - Classify as **Phenomenon A** (官网无内容).
   - Assign severity **P0**.
   - Do NOT proceed to Layer 2 for this question — there is no baseline to evaluate against.
   - Generate suggestion: "补充官方内容覆盖此问题".
3. For each question where `content_exists` is `true`:
   - Mark as eligible for Layer 2 evaluation.
   - Record the `official_urls` and `content_coverage` for use in Layer 2 prompts.
4. For each question where `content_exists` is `null` (unlabeled):
   - Log a warning: `"question {question_id} has no content_exists label, skipping"`.
   - Exclude from scoring.
5. Output a Layer 1 summary to stdout:
   ```
   Layer 1 — Content Completeness:
     Total questions: {n}
     Labeled: {labeled}
     Unlabeled (skipped): {unlabeled}
     Phenomenon A (no content): {a_count} → P0
     Eligible for Layer 2: {eligible}
   ```

**Step 3: Layer 2 — Citation Accuracy (LLM Evaluation)**

1. For each question eligible for Layer 2, iterate over all platform responses.
2. For each (question, platform) pair, construct an LLM evaluation prompt.
3. Read `references/scoring-prompt-template.md` for the full prompt template.
4. The prompt instructs the LLM to:
   - Identify all sources cited or referenced in the AI response (explicit URLs, named sources, implied references).
   - Classify each source as "official" (matching `official_urls` domains or known official channels) or "third-party".
   - Calculate `official_source_ratio` = official source count / total source count.
   - Determine which phenomenon (B/C/D/E) applies based on the classification rules in the prompt.
   - Assign an `accuracy_score` (1-10 scale).
   - Provide a brief `details` explanation.
5. Parse the LLM response. Run `python3 scripts/parse-llm-score.py '{llm_response_json}'` to extract and validate the structured scoring fields.
6. The script validates:
   - `citation_type` is one of B, C, D, E.
   - `official_source_ratio` is a float between 0.0 and 1.0.
   - `accuracy_score` is an integer 1-10.
   - All required fields are present.
7. If parsing fails, retry the LLM call once with a stricter format instruction. If it fails again, log the error and mark the pair as `"scoring_failed"`.

**Step 4: Assign Severity and Generate Suggestions**

1. For each scored (question, platform) pair, assign severity based on these rules:
   - **P0**: Phenomenon A (content gap) or C (wrong/hallucinated citation)
   - **P1**: Phenomenon B (has content, not cited) or E (low citation ratio, `official_source_ratio` < 0.3)
   - **P2**: Phenomenon D with minor issues (ratio > 0.7 but some inaccuracies noted)
   - **No action**: Phenomenon D, ratio > 0.7, no issues
2. For each actionable result (P0/P1/P2), generate a suggestion object:
   ```json
   {
     "suggestion_id": "s_001",
     "question_id": "q_001",
     "question": "...",
     "platform": "ChatGPT",
     "citation_type": "B",
     "official_source_ratio": 0.2,
     "accuracy_score": 4,
     "severity": "P1",
     "suggestion_text": "...",
     "category": "seo",
     "details": "..."
   }
   ```
3. Read `references/suggestion-rules.md` for category assignment logic and suggestion text templates.
4. Categories: `content` (A — missing content), `seo` (B — discoverability), `correction` (C — wrong info), `optimization` (E — low ratio).

**Step 5: Compile Output**

1. Assemble all results into `scoring-results.json`:
   ```json
   {
     "metadata": {
       "scored_at": "2026-03-12T...",
       "total_questions": 10,
       "total_platforms": 4,
       "total_pairs": 40,
       "scored_pairs": 36,
       "skipped_pairs": 4
     },
     "results": [
       {
         "question_id": "q_001",
         "platform": "ChatGPT",
         "content_exists": true,
         "citation_type": "B",
         "official_source_ratio": 0.2,
         "accuracy_score": 4,
         "severity": "P1",
         "details": "...",
         "sources_identified": [
           {"url": "...", "type": "official"},
           {"url": "...", "type": "third-party"}
         ]
       }
     ],
     "summary": {
       "by_phenomenon": {"A": 4, "B": 12, "C": 2, "D": 18, "E": 4},
       "by_severity": {"P0": 6, "P1": 16, "P2": 4, "no_action": 14},
       "by_platform": {
         "ChatGPT": {"avg_score": 6.2, "avg_ratio": 0.45},
         "DeepSeek": {"avg_score": 5.8, "avg_ratio": 0.38}
       }
     },
     "suggestions": []
   }
   ```
2. Write `scoring-results.json` to the project root.
3. Generate `suggestions.md` using the template in `assets/suggestions-template.md`. Fill in:
   - Executive summary (total scores, breakdown by phenomenon and severity).
   - Per-question detail tables.
   - Platform comparison matrix.
   - Prioritized action items grouped by severity.
4. Write `suggestions.md` to the project root.
5. Print a summary to stdout:
   ```
   Scoring complete:
     Pairs scored: {scored}/{total}
     P0: {p0} | P1: {p1} | P2: {p2} | OK: {ok}
     Avg citation ratio: {avg_ratio:.1%}
     Output: scoring-results.json, suggestions.md
   ```

**Step 6: Human Spot-Check Calibration**

1. PAUSE and inform the operator:
   ```
   Scoring complete. Please review scoring-results.json.
   Recommended: spot-check 20% of results (stratified by severity).
   Record corrections in scoring-calibration.md.
   ```
2. Run `python3 scripts/select-spot-check.py scoring-results.json` to generate a stratified sample for review.
3. The script outputs a Markdown checklist of (question_id, platform) pairs to review, sampling proportionally from each severity level.
4. After human review, any corrections saved to `scoring-calibration.md` will be incorporated as prompt context in the next scoring run (learning loop).

## Error Handling

* If `responses.json` is missing, abort with: `"responses.json not found. Run platform-sampler skill first."`
* If `content-labels.json` is missing, abort with: `"content-labels.json not found. Human labeling required before scoring."`
* If `content-labels.json` has all `content_exists: null`, abort with: `"No questions have been labeled. Complete human labeling first."`
* If LLM scoring fails for a (question, platform) pair after retry, log the error and continue. Report failed pairs in the summary.
* If more than 50% of pairs fail scoring, abort with: `"Too many scoring failures ({n}/{total}). Check LLM API availability."`
