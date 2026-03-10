---
name: keyword-generator
description: Generates a structured question set for GEO search assessment. Reads manual questions from a Markdown file, auto-generates industry discovery questions via LLM, extracts usage questions from community forums, and collects reverse questions from AI platforms. Merges all sources, deduplicates semantically, classifies by scenario and intent, then outputs questions.json and questions.md. Use when starting a new GEO assessment or refreshing the question set for a community. Do not use for platform sampling, scoring, or improvement suggestion generation.
---

# Keyword Generator

Generate a comprehensive question set covering two scenarios (了解阶段 + 使用阶段) for GEO search assessment.

## Prerequisites

- `.env` file with API tokens (copy from `.env.example` if missing)
- Community name and seed keywords provided as input

## Procedures

**Step 1: Load Configuration**

1. Read `.env` from the project root to load API tokens.
2. Accept two required inputs from the caller:
   - `community`: Community name (e.g., "MindSpore")
   - `seed_keywords`: Comma-separated seed keywords (e.g., "深度学习框架,AI计算,端侧推理")
3. Check if `feedback-rules.md` exists in the project root. If present, read it and incorporate the rules as additional prompt context for all LLM calls in subsequent steps.

**Step 2: Parse Manual Questions**

1. Check if `manual-questions.md` exists in the project root.
2. If present, run `python3 scripts/parse-manual-questions.py manual-questions.md` to extract questions.
3. The script outputs JSON to stdout. Capture the output as the manual question list.
4. If the file does not exist, skip this step with an empty manual question list.

**Step 3: Path 1 — Industry Question Discovery (了解阶段)**

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
3. Collect the output as the Path 1 question list.

**Step 4: Path 2 — Forum Usage Question Extraction (使用阶段)**

1. Check if MindSpore forum API is accessible. Read `references/forum-api-spec.md` for endpoint details.
2. If API is available, run `python3 scripts/fetch-forum-posts.py --community "{community}" --limit 50` to fetch top posts by view count.
3. If API is unavailable, prompt the LLM to generate representative usage questions:
   ```
   For the open-source community "{community}" with keywords "{seed_keywords}",
   generate typical usage questions that users would post on community forums.
   Cover: installation, configuration, training, deployment, migration, troubleshooting.
   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang.
   Generate 10-15 questions. Both zh and en.
   ```
4. If forum posts were fetched, prompt the LLM to rewrite them:
   ```
   Rewrite the following forum post titles into natural language search questions.
   Filter out pure bug reports. Keep questions relevant to GEO assessment.
   {forum_posts_json}
   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang, source_title.
   ```
5. Collect the output as the Path 2 question list.

**Step 5: Path 3 — AI Platform Reverse Extraction (使用阶段)**

1. For each available AI platform (check API tokens in `.env`):
   - Perplexity (PERPLEXITY_API_KEY)
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
6. Collect the output as the Path 3 question list.

**Step 6: Merge and Deduplicate**

1. Combine all question lists: manual + Path 1 + Path 2 + Path 3.
2. Prompt the LLM to perform semantic deduplication and classification:
   ```
   Merge the following question lists into a unified question set.
   Rules:
   - Remove semantically duplicate questions (similarity > 0.85). Keep the better-phrased version.
   - Manual questions have highest priority (keep all, mark source as "manual").
   - Classify each question:
     - scenario: "了解阶段" or "使用阶段"
     - intent: "认知" / "选型" / "趋势" / "场景" / "教程" / "故障" / "特性" / "迁移"
     - lang: "zh" or "en"
   - Target: 30-40 questions total.
   - If total exceeds 40, prioritize by: manual > multi-source > single-source.

   {all_questions_json}

   Output as JSON array with fields: id (q_001...), question, scenario, intent, lang, source, priority.
   ```
3. Validate the output with `python3 scripts/validate-questions.py` (reads from stdin).

**Step 7: Generate Output Files**

1. Write the validated JSON to `questions.json` in the project root.
2. Generate `questions.md` from the JSON using the template in `assets/questions-template.md`:
   - Group questions by scenario, then by intent.
   - Include a summary table at the top.
   - Mark source for each question (manual / path1 / path2 / path3).
3. Print a summary to stdout:
   ```
   Question set generated:
     Total: {count}
     了解阶段: {count_awareness}
     使用阶段: {count_usage}
     Sources: manual({n}), path1({n}), path2({n}), path3({n})
   Output: questions.json, questions.md
   ```

**Step 8: Human Review Checkpoint**

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
* If `scripts/fetch-forum-posts.py` fails (network error, API unavailable), fall back to LLM-generated usage questions (Step 4.3).
* If `scripts/call-ai-platform.py` fails for a specific platform, log the error and continue with remaining platforms. Path 3 requires at least 2 platforms to compute intersection.
* If `scripts/validate-questions.py` reports errors, display them and prompt the LLM to fix the JSON structure, then re-validate.
* If total question count is below 30 after dedup, prompt the LLM to generate additional questions to fill gaps in underrepresented intents.
