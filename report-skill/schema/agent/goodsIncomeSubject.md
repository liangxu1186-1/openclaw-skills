# /agent/goods/income-subject

状态：已实现

用于商品收入科目统计类问题。返回按收入科目聚合后的固定 `items` 列表，不暴露 legacy 动态表头和 `map` 结构。

## 请求参数

- `startTime`: 开始日期，例如 `20260401`
- `endTime`: 结束日期，例如 `20260430`
- `flag`: 时间口径，沿用现有业务定义；不传时默认 `2=营业日`

## 返回字段

- `items`
  - `incomeSubjectId`: 收入科目 ID
  - `incomeSubjectName`: 收入科目名称
  - `orderAmount`: 流水金额
  - `actualReceiptAmount`: 实收金额
  - `discountAmount`: 优惠金额

## 常见问法

- 商品收入科目统计
- 收入科目统计
- 商品收入科目构成

## 成功返回示例

```json
{
  "items": [
    {
      "incomeSubjectId": 3001,
      "incomeSubjectName": "正餐",
      "orderAmount": 4567.89,
      "actualReceiptAmount": 4200.00,
      "discountAmount": 367.89
    },
    {
      "incomeSubjectId": 3002,
      "incomeSubjectName": "茶饮",
      "orderAmount": 2789.10,
      "actualReceiptAmount": 2800.00,
      "discountAmount": 132.11
    }
  ]
}
```

## 使用规则

- 回答时优先看 `items` 前几项，概括主要收入科目和金额分布。
- 如果出现 `incomeSubjectId <= 0`，表示“未设置收入科目”。
- 若某项名称为空但 ID 正常，后端会回填为“异常收入科目N”。
- 默认保持简短，只给结论和少量关键点，不展开成长段分析。
