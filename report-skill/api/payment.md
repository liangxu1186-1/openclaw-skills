`report-skill` 的支付域接口目录。

支付域当前规划 2 个 `/agent/payment/...` 接口，其中 1 个已实现，1 个已定义待实现。

## 已实现接口

1. `/agent/payment/compose`
   适用问题：支付构成、支付类目和科目明细。
   详细字段：[../schema/agent/paymentCompose.md](../schema/agent/paymentCompose.md)

## 已定义待实现接口

1. `/agent/payment/discount-overview`
   适用问题：支付优惠数据。
   目标字段：[../schema/agent/paymentDiscountOverview.md](../schema/agent/paymentDiscountOverview.md)

## 使用规则

- 支付域接口统一只传 `startTime`、`endTime`、`flag`
- 支付域查询时间范围不能超过 `183` 天
- `payment/compose` 返回原始嵌套结构，先看顶层汇总，再看 `groupVoList` 和 `subjectVoList`
- `discount-overview` 当前会明确返回 `NOT_IMPLEMENTED`
