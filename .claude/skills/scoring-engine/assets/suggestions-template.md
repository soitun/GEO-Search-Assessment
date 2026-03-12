# GEO 评分报告

> 生成时间: {scored_at}

## 一、概览

| 指标 | 数值 |
|------|------|
| 评估问题数 | {total_questions} |
| 评估平台数 | {total_platforms} |
| 评估对数 | {scored_pairs}/{total_pairs} |
| 平均引用比例 | {avg_ratio:.1%} |

## 二、现象分布

| 现象 | 数量 | 占比 | 说明 |
|------|------|------|------|
| A — 官网无内容 | {a_count} | {a_pct:.0%} | 内容缺口，需补内容 |
| B — 有内容未引用 | {b_count} | {b_pct:.0%} | SEO/结构化优化 |
| C — 引用错误 | {c_count} | {c_pct:.0%} | 紧急纠错 |
| D — 引用比例大 | {d_count} | {d_pct:.0%} | 健康，持续监控 |
| E — 引用比例小 | {e_count} | {e_pct:.0%} | 内容深度优化 |

## 三、严重级别分布

| 级别 | 数量 | 说明 |
|------|------|------|
| P0 | {p0_count} | 立即行动 |
| P1 | {p1_count} | 计划改进 |
| P2 | {p2_count} | 低优先级 |
| 无需行动 | {ok_count} | 持续监控 |

## 四、平台对比

| 平台 | 平均得分 | 平均引用比例 | 主要现象 |
|------|---------|-------------|---------|
{platform_rows}

## 五、改进建议（按优先级）

### P0 — 立即行动

{p0_suggestions}

### P1 — 计划改进

{p1_suggestions}

### P2 — 低优先级

{p2_suggestions}

## 六、逐题详情

{question_details}

---

> 此报告由 GEO Search Assessment scoring-engine 自动生成。
> 建议人工抽检 20% 的评分结果，校准记录保存到 `scoring-calibration.md`。
