# /agent/marketing/activity-summary

状态：已实现

用于营销活动汇总类问题。返回 Java facade 原始业务 JSON。

## 请求参数

- `startTime`: 开始日期，例如 `20260401`
- `endTime`: 结束日期，例如 `20260430`
- `flag`: 时间口径，沿用现有业务定义；不传时默认 `2=营业日`

## 返回字段

- `sendNumPeople`: 发放人数
- `newCustomerPeople`: 新会员数
- `customerPeopleRate`: 拉新率
- `sendQuantity`: 礼品发放数量
- `verificationNum`: 核销数量
- `verificationRate`: 核销率
- `actualReceiptAmount`: 实收金额
- `customerCount`: 拉动客流
- `discountAmount`: 优惠金额
- `inputOutputRatio`: 投入产出比
- `orderTotalAmount`: 活动带动营业额
- `chainOrderTotalAmountRate`: 带动营业额比上期
- `chainActualReceiptAmountRate`: 带动实收比上期
- `chainSendNumPeopleRate`: 参与人数比上期
- `chainInputOutputRatioRate`: 投入产出比比上期
- `chainCustomerCountRate`: 拉动客流比上期
- `chainSendQuantityRate`: 礼品发放数比上期
- `chainDiscountAmountRate`: 核销成本比上期
- `updateTime`: 更新时间

## 使用规则

- 直接基于返回字段回答，不要在 skill 层重组 schema
- 默认保持简短，优先概括实收、客流、优惠和投入产出比
