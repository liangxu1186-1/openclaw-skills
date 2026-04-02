# /agent/order/refund

状态：已实现。

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `refundAmount`
- `refundOrderCount`
- `refundActualAmount`

## 常见问法

- 订单退款数据
- 本月退款金额
- 退款订单数

## 成功示例

```json
{
  "refundAmount": 123.45,
  "refundOrderCount": 6,
  "refundActualAmount": 120.00
}
```
