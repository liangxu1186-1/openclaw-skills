# /agent/order/shop-ranking

状态：已实现

用于门店榜单类问题。当前统一返回按营业额整理的门店榜单数据。

## 请求参数

- `startTime`
- `endTime`
- `flag`：不传时默认 `2=营业日`

## 返回字段

- `topStores`: 榜单列表
  - `shopName`
  - `amount`
  - `orderCount`

## 常见问法

- 本月门店榜单
- 今日门店排行
- 门店营业额榜

## 成功返回示例

```json
{
  "topStores": [
    {
      "shopName": "轻餐茶饮001",
      "amount": 349304.06,
      "orderCount": 287
    }
  ]
}
```

## 使用规则

- 当前榜单项字段只有 `shopName`、`amount`、`orderCount`。
- 回答榜首门店时，直接读取 `topStores[0]`。
- 该接口不再直接传 `metricsType`，也不允许 skill 自己拼 legacy 榜单参数。
