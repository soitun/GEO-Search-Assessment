---
name: issue-creator
description: Creates GitHub or GitCode Issues from GEO scoring results and improvement suggestions. Reads scoring-results.json or suggestions.md, maps each improvement item to a structured Issue (title, labels, body with phenomenon code and affected platforms), and creates them via GitHub or GitCode API. Auto-detects platform from repo URL. Requires GITHUB_TOKEN (for GitHub) or GITCODE_TOKEN (for GitCode). Use after scoring-engine completes and human review is done. Do not use for question generation, platform sampling, or scoring.
---

# Issue Creator

Create GitHub or GitCode Issues from GEO improvement suggestions, one Issue per actionable item.

## Prerequisites

- `.env` file with:
  - `GITHUB_TOKEN` — GitHub Personal Access Token with `issues:write` scope (for GitHub repos)
  - `GITCODE_TOKEN` — GitCode personal access token with `read_projects` + `write_issues` scopes (for GitCode repos)
- `scoring-results.json` (output from scoring-engine skill)
- Human review of scoring results completed

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root.
2. Accept required and optional inputs from the caller:
   - `repo_url` (required): Full repository URL, e.g. `https://github.com/opensourceways/portal-mcp-servers` or `https://gitcode.com/mindspore/mindspore`
   - `input_file` (optional): Path to scoring results. Default: `scoring-results.json`
   - `dry_run` (optional): If `true`, generate Issue payloads but do not POST to API. Default: `false`
3. **Auto-detect platform** from `repo_url`:
   - URL contains `github.com` → platform = `github`, load `GITHUB_TOKEN`
   - URL contains `gitcode.com` → platform = `gitcode`, load `GITCODE_TOKEN`
   - Extract `owner` and `repo` from the URL path.
4. If the required token is missing or empty, abort:
   - GitHub: `"GITHUB_TOKEN not set. Cannot create Issues."`
   - GitCode: `"GITCODE_TOKEN not set. Cannot create Issues."`
5. Read `references/gitcode-api-spec.md` for API endpoint details.

**Step 2: Parse Scoring Results**

1. Read the `input_file` (default: `scoring-results.json`).
2. Run `python3 scripts/parse-suggestions.py {input_file}` to extract actionable items.
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

   Output as JSON array with fields: group_id, title_summary, severity, citation_types, affected_platforms, question_ids, merged_suggestion_text, category, catalog_refs.
   ```
2. Collect the grouped suggestions.

**Step 4: Generate Issue Payloads**

1. For each grouped suggestion, construct an Issue payload using the template in `assets/issue-template.md`:
   - **Title**: `[GEO-{severity}] {title_summary}`
   - **Labels**: `geo-improvement`, `{severity}`, `{category}`
   - **Body**: Read `assets/issue-template.md` and fill in the template variables.
2. Run `python3 scripts/create-issue.py --owner {owner} --repo {repo} --platform {github|gitcode} --payload '{json}' [--dry-run]` for each Issue.
3. The script behavior:
   - **GitHub**: POSTs to `api.github.com/repos/{owner}/{repo}/issues`; auth via `Authorization: Bearer {token}`; labels as JSON array.
   - **GitCode**: POSTs to `api.gitcode.com/api/v5/repos/{owner}/{repo}/issues`; auth via `access_token` body field; labels as comma-separated string.
   - **Label fallback**: If the API returns 403 or 422 due to non-existent labels, automatically retry the same request **without labels**. Log a warning: `"Labels not applied (insufficient permission or labels not found). Issue created without labels."`
   - **Dry-run**: Prints the payload to stdout without calling the API.

**Step 5: Output Summary**

1. Collect all created Issue URLs (or dry-run payloads).
2. Write `created-issues.json` to the same directory as `input_file`:
   ```json
   {
     "created_at": "2026-03-12T...",
     "mode": "live",
     "repo": "github.com/opensourceways/portal-mcp-servers",
     "issues": [
       {
         "group_id": "g_001",
         "severity": "P0",
         "title": "[GEO-P0] 补充官网安装文档的版本对照表",
         "url": "https://github.com/opensourceways/portal-mcp-servers/issues/23",
         "number": 23,
         "question_ids": ["q_001", "q_002"],
         "labels_applied": false
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
     Labels applied: {yes|no (insufficient permission)}
     Mode: {live|dry-run}
   Output: {output_path}/created-issues.json
   ```

## Error Handling

* If the required token is missing, abort immediately.
* If `input_file` is missing, abort with: `"File not found. Run scoring-engine skill first."`
* If `parse-suggestions.py` returns zero actionable items, print `"No actionable suggestions found. All scores are healthy."` and exit cleanly.
* If `create-issue.py` fails for a specific Issue after label fallback (HTTP error other than label-related 403/422), log the error and continue with remaining Issues. Report failed Issues in the summary.
* If labels fail (HTTP 403/422 on label fields), retry **without labels** and log a warning. Do NOT abort.
* In dry-run mode, no API calls are made — all payloads are printed to stdout for review.
