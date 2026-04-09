`report-skill` 的统一接口总目录。

这个文件只负责按业务域分流，不再承载单接口字段细节。单个接口的请求参数、计划返回字段和问法边界，统一看对应业务域 `api/*.md` 和 `schema/agent/*.md`。

## 业务域目录

1. 订单域：[order.md](./order.md)
   已实现：`/agent/order/overview`、`/agent/order/business-type`、`/agent/order/channel-type`、`/agent/order/refund`、`/agent/order/shop-ranking`、`/agent/order/meal-period`、`/agent/order/time-period`、`/agent/order/cashier-income`

2. 商品域：[goods.md](./goods.md)
   已实现：`/agent/goods/overview`、`/agent/goods/sales-ranking`、`/agent/goods/category-ranking`、`/agent/goods/refund-ranking`、`/agent/goods/gift-ranking`、`/agent/goods/income-subject`

3. 支付域：[payment.md](./payment.md)
   已实现：`/agent/payment/compose`
   已定义待实现：`/agent/payment/discount-overview`

4. 营销域：[marketing.md](./marketing.md)
   已实现：`/agent/marketing/promotion-summary`、`/agent/marketing/activity-summary`

5. 会员域：[member.md](./member.md)
   已实现：`/agent/member/overview`、`/agent/member/preference`

## 统一规则

- 请求参数统一为 `startTime`、`endTime`、`flag`
- 未传 `flag` 时，默认按 `2=营业日`
- 所有查询时间范围都不能超过 `90` 天
- 成功时只返回业务 JSON
- 错误时返回错误 JSON
- skill 不再直接调用 legacy `/report/...` 接口
- 已定义待实现接口当前会明确返回 `NOT_IMPLEMENTED`

## 时间参数约定

- `startTime`：开始日期，例如 `20260401`
- `endTime`：结束日期，例如 `20260430`
- `flag`：时间口径，沿用当前业务已有定义

## 成功返回说明

- 已实现接口返回已落地的业务 JSON
- 已定义待实现接口文档中的“计划返回字段”代表目标契约，不代表当前运行时已经返回这些字段

## 错误返回说明

错误时返回结构化 JSON，例如：

```json
{
  "success": false,
  "code": "NOT_IMPLEMENTED",
  "message": "/agent/payment/discount-overview 暂未实现",
  "path": "/agent/payment/discount-overview"
}
```
