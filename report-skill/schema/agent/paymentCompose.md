# /agent/payment/compose

状态：已实现

用于支付构成类问题。返回原始支付汇总 + 类目 + 科目嵌套结构。

## 请求参数

- `startTime`: 开始日期，例如 `20260401`
- `endTime`: 结束日期，例如 `20260430`
- `flag`: 时间口径，沿用现有业务定义；不传时默认 `2=营业日`

## 返回字段

- `orderNum`: 订单数
- `actualReceiptAmount`: 实收金额
- `vipSaleAmount`: 会员消费金额
- `giftCardSaleAmount`: 礼品卡消费金额
- `storeAmount`: 储值消费金额
- `groupVoList`: 支付类目列表
  - `paySubjectGroupCode`: 支付类目编码
  - `paySubjectGroupName`: 支付类目名称
  - `orderNum`: 类目订单数
  - `actualReceiptAmount`: 类目实收金额
  - `subjectVoList`: 支付科目列表
    - `paySubjectCode`: 支付科目编码
    - `paySubjectName`: 支付科目名称
    - `orderNum`: 科目订单数
    - `actualReceiptAmount`: 科目实收金额

## 使用规则

- 回答时先看顶层汇总，再看 `groupVoList`，最后看 `subjectVoList`
- 没有明确要求时，不需要把所有科目逐条展开
