# /agent/order/meal-period

状态：已实现

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `items`
  - `mealPeriod`
  - `timeId`
  - `actualReceiptAmount`
  - `saleOrderNum`
  - `customerNum`

## 成功返回示例

```json
{
  "items": [
    {
      "mealPeriod": "午餐",
      "timeId": 1,
      "actualReceiptAmount": 456.78,
      "saleOrderNum": 12,
      "customerNum": 15
    }
  ]
}
```

## 常见问法

- 订单餐段数据
- 销售餐段统计
- 早中晚餐段表现
