# /agent/order/cashier-income

状态：已实现

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `items`
  - `operatorId`
  - `operatorName`
  - `paymentAmount`
  - `actualReceiptAmount`
  - `useNum`

## 成功返回示例

```json
{
  "items": [
    {
      "operatorId": 99,
      "operatorName": "张三",
      "paymentAmount": 999.99,
      "actualReceiptAmount": 888.88,
      "useNum": 18
    }
  ]
}
```

## 常见问法

- 收银员收款统计
- 收银员收款排行
- 各收银员收款金额
