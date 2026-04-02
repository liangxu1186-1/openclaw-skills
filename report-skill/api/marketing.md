`report-skill` 的营销域接口目录。

营销域当前提供 2 个 `/agent/marketing/...` 接口，已全部实现。

## 已实现接口

1. `/agent/marketing/promotion-summary`
   适用问题：促销活动汇总、促销活动看板。
   字段说明：[../schema/agent/marketingPromotionSummary.md](../schema/agent/marketingPromotionSummary.md)

2. `/agent/marketing/activity-summary`
   适用问题：营销活动汇总、营销活动看板。
   字段说明：[../schema/agent/marketingActivitySummary.md](../schema/agent/marketingActivitySummary.md)

## 使用规则

- 营销域所有接口统一只传 `startTime`、`endTime`、`flag`
- 营销域查询时间范围不能超过 `183` 天
- `promotion-summary` 只返回外层汇总字段，不返回 `dayList`
- `activity-summary` 直接返回 Java facade 原始业务 JSON
