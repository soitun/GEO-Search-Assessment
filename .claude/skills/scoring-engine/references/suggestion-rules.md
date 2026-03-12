# Suggestion Rules

Rules for assigning categories and generating suggestion text based on phenomena type.

## Category Assignment

| Phenomenon | Category | Label |
|------------|----------|-------|
| A | `content` | 内容缺口 |
| B | `seo` | 可检索性不足 |
| C | `correction` | 引用错误 |
| D | — | 无需行动（或 `monitoring` 如有小瑕疵） |
| E | `optimization` | 引用比例不足 |

## Suggestion Text Templates

### Phenomenon A — Content Gap

```
【P0 内容缺口】问题「{question}」在官方渠道无对应内容。
建议：在官网/文档中补充此问题的完整解答。
优先级：P0（内容缺失是 AI 无法引用的根本原因）。
```

### Phenomenon B — Not Cited

```
【{severity} 可检索性不足】问题「{question}」官方有内容但 {platform} 未引用。
官方源引用比例: {ratio:.0%}。
建议：优化官方页面的 SEO 结构（标题、meta description、结构化数据），提升 AI 平台抓取优先级。
可参考官方页面: {official_urls}。
```

### Phenomenon C — Wrong Citation

```
【P0 引用错误】问题「{question}」在 {platform} 的回答引用了官方源但信息不准确。
具体问题: {details}。
建议：
1. 核查并更新官方页面中的相关信息，确保准确性。
2. 如为过时信息，在页面显著位置标注版本适用范围。
3. 考虑添加 structured data 标注内容更新日期。
```

### Phenomenon E — Low Ratio

```
【{severity} 引用比例低】问题「{question}」在 {platform} 的回答中官方源占比仅 {ratio:.0%}。
建议：
1. 丰富官方内容深度，覆盖更多子话题。
2. 增加内部交叉链接，提升官方内容权威性信号。
3. 确保官方页面内容比第三方源更全面、更新。
```

## Severity Override Rules

- If `citation_type` is C, severity is always P0 regardless of ratio.
- If `citation_type` is B and `content_coverage` is "full", elevate to P1 (official has complete answer but AI ignores it).
- If `citation_type` is E and `official_source_ratio` < 0.1, elevate to P1.
- Phenomenon D with `accuracy_score` >= 8 → no_action.
- Phenomenon D with `accuracy_score` < 8 → P2.
