---
name: get-question
description: Generates a structured question set for GEO search assessment. Supports 4 question source paths (forum, issue, industry, AI reverse) — select individually or all. Reads manual questions from Markdown, auto-generates questions via selected paths, merges, deduplicates semantically, classifies by scenario and intent, then outputs questions.json and questions.md. Forum and issue are the primary sources. Use when starting a new GEO assessment or refreshing the question set for a community. Do not use for platform sampling, scoring, or improvement suggestion generation.
---

# Get Question

Generate a comprehensive question set covering two scenarios (了解阶段 + 使用阶段) for GEO search assessment.

## Prerequisites

- `.env` file with API tokens (copy from `.env.example` if missing)
- Community name and seed keywords provided as input

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root to load API tokens.
2. Accept required and optional inputs from the caller:
   - `community` (required): Community name (e.g., "MindSpore")
   - `seed_keywords` (required): Comma-separated seed keywords (e.g., "深度学习框架,AI计算,端侧推理")
   - `paths` (optional): Comma-separated list of paths to run. Options: `forum`, `issue`, `industry`, `ai_reverse`, `all`. Default: `all`.
     - `forum` → Path 1: Forum Usage Question Extraction (primary source)
     - `issue` → Path 2: Repo Issue Question Extraction (primary source)
     - `industry` → Path 3: Industry Question Discovery
     - `ai_reverse` → Path 4: AI Platform Reverse Extraction
     - `all` → Run all four paths
3. Check if `feedback-rules.md` exists in the project root. If present, read it and incorporate the rules as additional prompt context for all LLM calls in subsequent steps.
4. Log which paths are selected: `"Running paths: {paths}"`

**Step 2: Parse Manual Questions**

1. Check if `manual-questions.md` exists in the project root.
2. If present, run `python3 scripts/parse-manual-questions.py manual-questions.md` to extract questions.
3. The script outputs JSON to stdout. Capture the output as the manual question list.
4. If the file does not exist, skip this step with an empty manual question list.

**Step 3: Path 1 — Forum Usage Question Extraction (使用阶段) [PRIMARY]**

> This is the primary question source. Forum and issue data reflect real developer pain points.
> Only runs if `paths` includes `forum` or `all`.

1. Run `python3 scripts/fetch-forum-posts.py --community "{community}" --limit 50` to fetch top topics from the MindSpore Discourse forum (`https://discuss.mindspore.cn`).
   - The script fetches from `问题求助 Help` (id:4) and `MindSpore Lite` (id:38) categories, plus global top topics.
   - Topics are deduplicated, sorted by views, pinned/closed topics excluded.
   - See `references/forum-api-spec.md` for full API details.
2. If the script succeeds, prompt the LLM to rewrite forum topics into search questions:
   ```
   The following are real forum post titles from the {community} community, sorted by views.
   Rewrite them into natural language search questions that a developer might type into an AI assistant.

   Rules:
   - Filter out pure bug reports (e.g., "xxx报错" with no general learning value).
   - Keep questions that represent common usage scenarios, installation issues, configuration questions, and feature inquiries.
   - Preserve the original intent — do not generalize too much.
   - For each question, classify the category: installation, configuration, training, deployment, migration, troubleshooting, feature, performance.

   {forum_posts_json}

   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang, source_title, source_views.
   ```
3. If the script fails (network error, API unavailable), fall back to LLM-generated usage questions:
   ```
   For the open-source community "{community}" with keywords "{seed_keywords}",
   generate typical usage questions that users would post on community forums.
   Cover: installation, configuration, training, deployment, migration, troubleshooting.
   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang.
   Generate 10-15 questions. Both zh and en.
   ```
4. Collect the output as the Path 1 question list.

**Step 4: Path 2 — Repo Issue Question Extraction (使用阶段) [PRIMARY]**

> This is a primary question source alongside forum. Repo issues reflect real developer problems.
> Only runs if `paths` includes `issue` or `all`.
> Requires `GITCODE_TOKEN` in `.env`.

1. Run `python3 scripts/fetch-repo-issues.py --owner mindspore --repo mindspore --limit 50` to fetch issues from GitCode (`https://gitcode.com/mindspore/mindspore/issues`).
   - The script calls GitCode API v5 (`api.gitcode.com`) with token auth.
   - Issues are sorted by comment count (engagement proxy).
   - See `references/gitcode-api-spec.md` for full API details.
2. If the script succeeds, prompt the LLM to rewrite issue titles into search questions:
   ```
   The following are real issue titles from the {community} repository on GitCode, sorted by engagement (comments).
   Rewrite them into natural language search questions that a developer might type into an AI assistant.

   Rules:
   - Filter out pure bug reports with only error stack traces and no general learning value.
   - Keep issues that represent common usage problems, feature requests, compatibility questions, and how-to questions.
   - Preserve the original intent — do not generalize too much.
   - For each question, classify the category: installation, configuration, training, deployment, migration, troubleshooting, feature, performance, compatibility.

   {issues_json}

   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang, source_title, source_comments.
   ```
3. If the script fails (no token, network error, API error), log warning and skip this path. Do NOT fall back to LLM generation — issue data should come from real sources.
4. Collect the output as the Path 2 question list.

**Step 5: Path 3 — Industry Question Discovery (了解阶段)**

> Only runs if `paths` includes `industry` or `all`.

1. Determine the community's domain hierarchy by prompting the LLM:
   ```
   Given the open-source community "{community}" with keywords "{seed_keywords}",
   determine:
   - Industry (行业)
   - Sub-domain (细分领域)
   - Positioning (定位)
   - Competitors (竞品, list 3-5)
   Output as JSON.
   ```
2. Using the domain hierarchy, generate questions across four user intents by prompting the LLM:
   ```
   Based on the following domain hierarchy:
   {domain_hierarchy_json}

   Generate search questions a user might ask when they do NOT know about {community}.
   Cover four intent categories:
   - 认知 (awareness): "What are the mainstream X?" type questions
   - 选型 (selection): "Which X should I choose?" type questions
   - 趋势 (trends): "What are the trends in X?" type questions
   - 场景 (scenarios): "What X works best for Y scenario?" type questions

   Also generate reverse-expansion questions using competitors:
   - "What alternatives to {competitor} exist?" type questions

   Output as JSON array with fields: question, intent, scenario ("了解阶段"), lang.
   Generate 10-15 questions total. Both zh and en.
   ```
3. Collect the output as the Path 2 question list.

**Step 6: Path 4 — AI Platform Reverse Extraction (使用阶段)**

> Only runs if `paths` includes `ai_reverse` or `all`.

1. For each available AI platform (check API tokens in `.env`):
   - ChatGPT (OPENAI_API_KEY)
   - DeepSeek (DEEPSEEK_API_KEY)
   - 豆包 (DOUBAO_API_KEY)
   - Qwen (QWEN_API_KEY)
2. Send two queries to each platform:
   - "关于{community}最常被问到的问题有哪些？请列出10个。"
   - "What are the most frequently asked questions about {community}? List 10."
3. Run `python3 scripts/call-ai-platform.py --platform {name} --api-key {key} --query "{query}"` for each call.
4. Collect all returned question lists.
5. Prompt the LLM to find the intersection (questions mentioned by 2+ platforms rank higher):
   ```
   The following question lists were collected from different AI platforms:
   {all_platform_questions_json}

   Find common questions (semantically similar across 2+ platforms).
   Rank by frequency. Output as JSON array with fields: question, mentioned_by_count, scenario ("使用阶段"), lang.
   ```
6. Collect the output as the Path 4 question list.

**Step 7: Merge and Deduplicate**

1. Combine all question lists: manual + Path 1 + Path 2 + Path 3 + Path 4.
2. Prompt the LLM to perform semantic deduplication and classification:
   ```
   Merge the following question lists into a unified question set.
   Rules:
   - Remove semantically duplicate questions (similarity > 0.85). Keep the better-phrased version.
   - Manual questions have highest priority (keep all, mark source as "manual").
   - Forum-sourced questions (Path 1) and issue-sourced questions (Path 2) have second-highest priority.
   - Classify each question:
     - scenario: "了解阶段" or "使用阶段"
     - intent: "认知" / "选型" / "趋势" / "场景" / "教程" / "故障" / "特性" / "迁移"
     - lang: "zh" or "en"
   - Target: 30-40 questions total.
   - If total exceeds 40, prioritize by: manual > forum (path1) / issue (path2) > multi-source > single-source.

   {all_questions_json}

   Output as JSON array with fields: id (q_001...), question, scenario, intent, lang, source, priority.
   ```
3. Validate the output with `python3 scripts/validate-questions.py` (reads from stdin).

**Step 8: Generate Output Files**

1. Write the validated JSON to `questions.json` in the project root.
2. Generate `questions.md` from the JSON using the template in `assets/questions-template.md`:
   - Group questions by scenario, then by intent.
   - Include a summary table at the top.
   - Mark source for each question (manual / path1-forum / path2-issue / path3-industry / path4-ai_reverse).
3. Print a summary to stdout:
   ```
   Question set generated:
     Total: {count}
     了解阶段: {count_awareness}
     使用阶段: {count_usage}
     Sources: manual({n}), path1-forum({n}), path2-issue({n}), path3-industry({n}), path4-ai_reverse({n})
   Paths run: {paths_run}
   Output: questions.json, questions.md
   ```

**Step 9: Human Review Checkpoint**

1. PAUSE execution and display:
   ```
   ⏸ Human review checkpoint.
   Please review questions.md and provide feedback.
   - Delete questions that are not relevant.
   - Add missing questions.
   - Note any patterns to avoid/prefer in the future.

   After review, save feedback to feedback-rules.md.
   Then resume to continue the workflow.
   ```
2. Wait for the user to signal completion.

## Error Handling

* If `.env` is missing or API tokens are empty, warn and skip the corresponding platform in Path 3. Continue with available platforms.
* If `scripts/fetch-forum-posts.py` fails (network error, API unavailable), fall back to LLM-generated usage questions (Step 3.3).
* If `scripts/fetch-repo-issues.py` fails (no GITCODE_TOKEN, network error, API error), log warning and skip Path 2. Do not fall back to LLM generation.
* If `scripts/call-ai-platform.py` fails for a specific platform, log the error and continue with remaining platforms. Path 4 requires at least 2 platforms to compute intersection.
* If `scripts/validate-questions.py` reports errors, display them and prompt the LLM to fix the JSON structure, then re-validate.
* If total question count is below 30 after dedup, prompt the LLM to generate additional questions to fill gaps in underrepresented intents.
* If only a subset of paths was selected and total count is low, that is expected — do not auto-fill unless below 10.
