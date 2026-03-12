# GEO Improvement Report Template

Use this structure when generating `improvement-report.md`.

## Structure

```markdown
# {Community} GEO Improvement Report

> Generated: {date}
> Questions analyzed: {question_count}
> Platforms: {platform_list}
> Recognized citation sources: {official_domains}

---

## 1. Executive Summary

### Overall Health
- Total responses analyzed: {total}
- Accuracy distribution: {severity_chart}
- Top failure patterns: {top_3_patterns}

### Key Findings
1. {finding_1}
2. {finding_2}
3. {finding_3}

---

## 2. Per-Question Analysis

### Q{id}: {question_text}

**Official Answer Summary:** {standard_answer_summary}

| Platform | Accuracy | Citations (Official) | Failure Mode | Severity |
|----------|----------|---------------------|--------------|----------|
| {platform} | {score}/5 | {official}/{total} | {mode} | {severity} |

**Key Issues:**
- {issue_description}

**Suggestions:**
| ID | Category | Change | Priority |
|----|----------|--------|----------|
| {id} | {category} | {recommended_change} | {priority} |

(Repeat for each question)

---

## 3. Universal Recommendations

### 3.1 {Dimension Title}

**Evidence:** {reference to specific diagnostic findings}

**Recommendations:**
| ID | Title | Description | Priority | Scope |
|----|-------|-------------|----------|-------|
| {id} | {title} | {description} | {priority} | {scope} |

(Repeat for each dimension with findings)

---

## 4. Execution Roadmap

### Phase 1: Immediate (1-2 weeks) — P0 Items
- [ ] {P0_item_1}
- [ ] {P0_item_2}

### Phase 2: Short-term (2-4 weeks) — P1 Items
- [ ] {P1_item_1}
- [ ] {P1_item_2}

### Phase 3: Ongoing — P2 Items
- [ ] {P2_item_1}

---

## 5. KPI Tracking

| Metric | Definition | Current | Target |
|--------|-----------|---------|--------|
| Official citation rate | % of responses citing official sources | {current}% | ≥60% |
| Factual accuracy rate | % of responses matching standard answer | {current}% | ≥80% |
| Negation transmission rate | % of negative facts correctly conveyed | {current}% | ≥70% |
| Context correctness rate | % of terms correctly identified in product context | {current}% | ≥90% |
| Version freshness rate | % of citations to stable/latest version | {current}% | ≥70% |

---

## Appendix

- Data sources: {file_list}
- Evaluation criteria: {criteria_description}
```

## Formatting Rules

- Use tables for comparisons and multi-item lists
- Use bold for emphasis on key findings
- Priority tags: `P0` (critical), `P1` (high), `P2` (medium)
- Severity levels: none, low, medium, high, critical
- All suggestion IDs use format: QS-001 (per-question) or US-001 (universal)
