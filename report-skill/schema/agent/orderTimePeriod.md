# /agent/order/time-period

状态：已实现

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `items`
  - `period`
  - `periodStart`
  - `orderAmount`
  - `actualReceiptAmount`
  - `saleOrderNum`
  - `customerNum`

## 成功返回示例

```json
{
  "items": [
    {
      "period": "10:00 - 11:00:00",
      "periodStart": "10:00",
      "orderAmount": 888.88,
      "actualReceiptAmount": 800.00,
      "saleOrderNum": 20,
      "customerNum": 25
    }
  ]
}
```

## 常见问法

- 订单时段数据
- 销售时段统计
- 各时段订单表现
