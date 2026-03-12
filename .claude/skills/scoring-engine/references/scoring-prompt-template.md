# Scoring Prompt Template

Use this template to construct the LLM evaluation prompt for each (question, platform) pair in Layer 2.

## Prompt

```
你是一个 GEO（Generative Engine Optimization）评分专家。请分析以下 AI 平台回答，评估其对官方内容的引用准确性。

## 待评估信息

**问题**: {question}
**平台**: {platform}
**AI 回答**:
{response_text}

**官方内容参考**:
- 内容覆盖度: {content_coverage}
- 官方 URL: {official_urls}

{calibration_context}

## 评估任务

1. **识别来源**: 列出回答中引用或提及的所有信息来源（显式 URL、命名来源、隐含引用）。
2. **分类来源**: 将每个来源标记为 "official"（匹配以下官方域名）或 "third-party"。
   - 官方域名: mindspore.cn, gitcode.com/mindspore, github.com/mindspore-ai, gitee.com/mindspore
3. **计算引用比例**: official_source_ratio = 官方源数量 / 总来源数量（如无来源，ratio = 0）。
4. **判定现象类型**:
   - **B（有内容未引用）**: 官方有内容，但回答未引用或未提及任何官方源。ratio = 0 或极低。
   - **C（引用错误信息）**: 回答引用了官方源但信息不准确（版本错误、过时信息、与官方内容矛盾）。这是最严重的问题。
   - **D（引用比例大）**: 回答主要引用官方源，信息准确。ratio > 0.5。
   - **E（引用比例小）**: 回答引用了官方源但比例低。0 < ratio ≤ 0.5。
5. **评分**: 给出 1-10 分的 accuracy_score:
   - 9-10: 主要引用官方源，信息完全准确
   - 7-8: 引用官方源，信息基本准确但有小瑕疵
   - 5-6: 部分引用官方源，或信息有遗漏
   - 3-4: 很少引用官方源，主要依赖第三方信息
   - 1-2: 未引用官方源，或引用了错误信息

## 输出格式

严格按以下 JSON 格式输出，不要添加任何其他内容:

{
  "citation_type": "B|C|D|E",
  "official_source_ratio": 0.0-1.0,
  "accuracy_score": 1-10,
  "details": "一句话说明判定理由",
  "sources_identified": [
    {"url_or_name": "来源名称或URL", "type": "official|third-party"}
  ]
}
```

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{question}` | `responses.json` → `question` | Original question text |
| `{platform}` | `responses.json` → `platform` | AI platform name |
| `{response_text}` | `responses.json` → `response_text` | Full AI response |
| `{content_coverage}` | `content-labels.json` → `content_coverage` | full / partial |
| `{official_urls}` | `content-labels.json` → `official_urls` | Comma-separated official URLs |
| `{calibration_context}` | `scoring-calibration.md` (if exists) | Human correction context from prior rounds |

## Calibration Context Format

When `scoring-calibration.md` exists, insert this block:

```
## 校准上下文（来自人工抽检）

以下是之前评分中人工校准的修正记录，请参考这些修正避免类似偏差：

{calibration_entries}
```

If no calibration file exists, omit this block entirely.
