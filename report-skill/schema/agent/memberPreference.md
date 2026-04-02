# /agent/member/preference

状态：已实现

用于会员偏好类问题。保持单接口返回三块数据，不拆成三个 tool call。

## 请求参数

- `startTime`
- `endTime`
- `flag`：不传时默认 `2=营业日`

## 返回字段

- `favoriteGoods`
  - `goodsName`
  - `goodsNum`
- `favoriteStores`
  - `shopName`
  - `amount`
- `favoritePractices`
  - `practice`
  - `count`

## 常见问法

- 本月会员喜好商品
- 会员消费门店
- 会员消费门店排行
- 会员口味偏好
- 会员最喜爱商品和门店

## 成功返回示例

```json
{
  "favoriteGoods": [
    {
      "goodsName": "茉莉醒脑系列",
      "goodsNum": 5666
    }
  ],
  "favoriteStores": [
    {
      "shopName": "轻餐茶饮001",
      "amount": 341830.01
    }
  ],
  "favoritePractices": [
    {
      "practice": "正常冰",
      "count": 1983
    }
  ]
}
```

## 使用规则

- `favoriteGoods` 表示会员最喜爱商品。
- `favoriteStores` 表示会员消费门店；如果用户问“会员消费门店排行”，直接基于这块回答。
- `favoritePractices` 表示会员最喜爱口味做法。
- 回答时按三块分别说明；不要把某一块为空解释成整个接口无数据。
- 默认最多输出 1 句总结 + 3 条要点，分别覆盖商品、门店、口味。
- 没有明确要求时，不主动补“原因分析”“优化建议”“继续查询建议”。
