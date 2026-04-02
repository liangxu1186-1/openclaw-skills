# /agent/order/channel-type

状态：已实现。

## 请求参数

- `startTime`
- `endTime`
- `flag`

## 返回字段

- `items`
  - `channelType`
  - `channelTypeName`
  - `orderAmount`
  - `orderCount`
  - `customerCount`
  - `actualReceiptAmount`

## 常见问法

- 按订单渠道类型分组
- 订单渠道统计
- 各渠道营业额

## 成功示例

```json
{
  "items": [
    {
      "channelType": 2,
      "channelTypeName": "外卖",
      "orderAmount": 2345.67,
      "orderCount": 23,
      "customerCount": 30,
      "actualReceiptAmount": 2100.12
    }
  ]
}
```
