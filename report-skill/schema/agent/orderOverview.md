# /agent/order/overview

状态：已实现

用于订单总览类问题。当前是 `report-skill` 里查询营业额、含待结账营业额、待结账金额、未落单金额、实收、优惠、优惠率、退款、退货单数、订单数、客流的统一接口。

## 请求参数

- `startTime`: 开始日期，例如 `20260401`
- `endTime`: 结束日期，例如 `20260430`
- `flag`: 时间口径，沿用现有业务定义；不传时默认 `2=营业日`

## 返回字段

- `orderAmount`: 营业额
- `incUnPayOrderAmount`: 营业额（包含待结账）
- `unPayOrderAmount`: 待结账金额
- `unLdTotalAmount`: 未落单金额
- `refundActualAmount`: 退货实退金额
- `actualReceiptAmount`: 实收金额
- `discountAmount`: 优惠金额
- `discountRate`: 优惠占比
- `refundAmount`: 退款金额
- `saleOrderNum`: 有效订单数
- `orderCount`: 订单数
- `refundOrderNum`: 退货单数
- `refundOrderCount`: 退货单数
- `customerNum`: 客流量
- `customerCount`: 客流数

## 常见问法

- 今日营业额
- 本月营业额
- 今日实收
- 本月订单数
- 今日客流

## 成功返回示例

```json
{
  "orderAmount": 1399.86,
  "incUnPayOrderAmount": 1499.86,
  "unPayOrderAmount": 100.00,
  "unLdTotalAmount": 20.00,
  "refundActualAmount": 18.50,
  "actualReceiptAmount": 1240.60,
  "discountAmount": 159.26,
  "discountRate": 0.1138,
  "refundAmount": 21.00,
  "saleOrderNum": 45,
  "orderCount": 45,
  "refundOrderNum": 3,
  "refundOrderCount": 3,
  "customerNum": 53,
  "customerCount": 53
}
```

## 使用规则

- 成功时直接返回以上业务 JSON 字段。
- `saleOrderNum/refundOrderNum/customerNum` 是原始总览字段；`orderCount/refundOrderCount/customerCount` 是当前 agent 契约里的兼容别名。
- 错误时返回错误 JSON，不要把调用失败误说成“无数据”。
- 该接口只回答总览指标，不负责门店排行、会员偏好、商品排行。
