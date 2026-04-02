`report-skill` 的订单域接口目录。

订单域当前共有 8 个 `/agent/order/...` 接口，当前已全部实现。

## 已实现接口

1. `/agent/order/overview`
   适用问题：营业额、含待结账营业额、待结账金额、未落单金额、实收、优惠、优惠率、退款、退货单数、订单数、客流。
   详细字段：[../schema/agent/orderOverview.md](../schema/agent/orderOverview.md)

2. `/agent/order/business-type`
   适用问题：按照订单业务类型分组。
   详细字段：[../schema/agent/orderBusinessType.md](../schema/agent/orderBusinessType.md)

3. `/agent/order/channel-type`
   适用问题：按照订单渠道类型分组。
   详细字段：[../schema/agent/orderChannelType.md](../schema/agent/orderChannelType.md)

4. `/agent/order/refund`
   适用问题：订单退款数据。
   详细字段：[../schema/agent/orderRefund.md](../schema/agent/orderRefund.md)

5. `/agent/order/shop-ranking`
   适用问题：门店榜单、门店排行、门店营业额榜。
   详细字段：[../schema/agent/orderShopRanking.md](../schema/agent/orderShopRanking.md)

6. `/agent/order/meal-period`
   适用问题：订单餐段数据。
   详细字段：[../schema/agent/orderMealPeriod.md](../schema/agent/orderMealPeriod.md)

7. `/agent/order/time-period`
   适用问题：订单时段数据。
   详细字段：[../schema/agent/orderTimePeriod.md](../schema/agent/orderTimePeriod.md)

8. `/agent/order/cashier-income`
   适用问题：收银员收款统计。
   详细字段：[../schema/agent/orderCashierIncome.md](../schema/agent/orderCashierIncome.md)

## 使用规则

- 订单域所有接口统一只传 `startTime`、`endTime`、`flag`
- 订单域查询时间范围不能超过 `183` 天
- 不再向 skill 暴露 legacy `stime/etime/dateType/startDate/endDate/metricsType`
