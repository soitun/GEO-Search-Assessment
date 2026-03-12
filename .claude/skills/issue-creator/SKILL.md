---
name: issue-creator
description: Creates GitCode Issues from GEO scoring results and improvement suggestions. Reads scoring-results.json or suggestions.md, maps each improvement item to a structured Issue (title, labels, body with phenomenon code and affected platforms), and creates them via GitCode API. Requires GITCODE_TOKEN. Use after scoring-engine completes and human review is done. Do not use for question generation, platform sampling, or scoring.
---

# Issue Creator

Create GitCode Issues from GEO improvement suggestions, one Issue per actionable item.

## Prerequisites

- `.env` file with `GITCODE_TOKEN` (GitCode API personal access token with `read_projects` + `write_issues` scopes)
- `scoring-results.json` in the project root (output from scoring-engine skill)
- Human review of scoring results completed

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root to load `GITCODE_TOKEN`.
2. If `GITCODE_TOKEN` is missing or empty, abort with error: `"GITCODE_TOKEN not set. Cannot create Issues."`
3. Accept required and optional inputs from the caller:
   - `owner` (required): Repository owner (default: `mindspore`)
   - `repo` (required): Repository name (default: `mindspore`)
   - `input_file` (optional): Path to scoring results. Default: `scoring-results.json`
   - `dry_run` (optional): If `true`, generate Issue payloads but do not POST to API. Default: `false`
4. Read `references/gitcode-api-spec.md` for API endpoint details.

**Step 2: Parse Scoring Results**

1. Read `scoring-results.json` from the project root.
2. Run `python3 scripts/parse-suggestions.py scoring-results.json` to extract actionable items.
3. The script outputs a JSON array of suggestion objects to stdout:
   ```json
   [
     {
       "suggestion_id": "s_001",
       "question_id": "q_001",
       "question": "MindSpore 支持哪些安装方式？",
       "citation_type": "B",
       "severity": "P1",
       "affected_platforms": ["ChatGPT", "DeepSeek"],
       "suggestion_text": "...",
       "category": "seo"
     }
   ]
   ```
4. If the file is missing or the script fails, abort with a clear error.

**Step 3: Deduplicate and Group**

1. Prompt the LLM to deduplicate and group similar suggestions:
   ```
   The following are GEO improvement suggestions extracted from scoring results.
   Group semantically similar suggestions that target the same root cause.

   Rules:
   - Merge suggestions that recommend the same action (e.g., "add install docs" appearing for multiple platforms).
   - Keep the highest severity when merging (P0 > P1 > P2).
   - Combine affected_platforms lists.
   - Preserve all question_ids involved.
   - Each group becomes one Issue.

   {suggestions_json}

   Output as JSON array with fields: group_id, title_summary, severity, citation_types, affected_platforms, question_ids, merged_suggestion_text, category.
   ```
2. Collect the grouped suggestions.

**Step 4: Generate Issue Payloads**

1. For each grouped suggestion, construct an Issue payload using the template in `assets/issue-template.md`:
   - **Title**: `[GEO-{severity}] {title_summary}`
   - **Labels**: `geo-improvement`, `{severity}`, `{category}`
   - **Body**: Read `assets/issue-template.md` and fill in the template variables.
2. Run `python3 scripts/create-issue.py --owner {owner} --repo {repo} --payload '{json}' [--dry-run]` for each Issue.
3. The script:
   - In normal mode: POSTs to `api.gitcode.com/api/v5/repos/{owner}/{repo}/issues` and returns the created Issue URL.
   - In dry-run mode: Prints the payload to stdout without calling the API.

**Step 5: Output Summary**

1. Collect all created Issue URLs (or dry-run payloads).
2. Write `created-issues.json` to the project root:
   ```json
   {
     "created_at": "2026-03-12T...",
     "mode": "live",
     "issues": [
       {
         "group_id": "g_001",
         "severity": "P0",
         "title": "[GEO-P0] 补充官网安装文档的版本对照表",
         "url": "https://gitcode.com/mindspore/mindspore/issues/IXXXX",
         "question_ids": ["q_001", "q_002"]
       }
     ]
   }
   ```
3. Print a summary to stdout:
   ```
   Issues created:
     Total: {count}
     P0: {p0_count}
     P1: {p1_count}
     P2: {p2_count}
     Mode: {live|dry-run}
   Output: created-issues.json
   ```

## Error Handling

* If `GITCODE_TOKEN` is missing, abort immediately. Do not proceed without authentication.
* If `scoring-results.json` is missing, abort with: `"scoring-results.json not found. Run scoring-engine skill first."`
* If `scripts/parse-suggestions.py` returns zero actionable items, print `"No actionable suggestions found. All scores are healthy."` and exit cleanly.
* If `scripts/create-issue.py` fails for a specific Issue (HTTP error), log the error and continue with remaining Issues. Report failed Issues in the summary.
* If GitCode API returns 403 (insufficient scopes), suggest the user check their token permissions.
* In dry-run mode, no API calls are made — all payloads are printed to stdout for review.
