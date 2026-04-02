# /agent/order/business-type

状态：已实现

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `items`
  - `businessType`
  - `businessTypeName`
  - `orderAmount`
  - `orderCount`
  - `customerCount`
  - `actualReceiptAmount`

## 成功返回示例

```json
{
  "items": [
    {
      "businessType": 3,
      "businessTypeName": "堂食",
      "orderAmount": 2345.67,
      "orderCount": 23,
      "customerCount": 30,
      "actualReceiptAmount": 2200.10
    }
  ]
}
```
## 常见问法

- 按订单业务类型分组
- 订单业务类型统计
- 业务类型营业额
