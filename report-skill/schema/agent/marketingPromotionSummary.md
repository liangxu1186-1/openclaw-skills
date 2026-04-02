# /agent/marketing/promotion-summary

状态：已实现

用于促销活动汇总类问题。返回促销汇总外层字段，不返回趋势 `dayList`。

## 请求参数

- `startTime`: 开始日期，例如 `20260401`
- `endTime`: 结束日期，例如 `20260430`
- `flag`: 时间口径，沿用现有业务定义；不传时默认 `2=营业日`

## 返回字段

- `discountAmount`: 活动成本
- `discountRate`: 优惠占比
- `orderAmount`: 活动带动流水
- `orderTotalAmount`: 订单金额
- `actualReceiptAmount`: 活动带动实收
- `orderNum`: 拉动订单数
- `executeNum`: 执行次数
- `customNum`: 拉动客流
- `unitPrice`: 客单价
- `promotionEffort`: 促销力度
- `roi`: 投入产出比
- `promotionOrderNum`: 活动订单量
- `promotionGoodsNum`: 活动商品量
- `upOrderNum`: 订单数比上期
- `upOrderAmount`: 流水比上期
- `upActualReceiptAmount`: 实收比上期
- `upDiscountAmount`: 活动成本比上期
- `upUnitPrice`: 客单价比上期
- `upCustomNum`: 客流比上期
- `upPromotionEffort`: 促销力度比上期
- `upRoi`: 投入产出比比上期
- `updateTime`: 更新时间

## 使用规则

- 这是汇总接口，不要假设会返回趋势日线
- 回答时优先概括流水、实收、优惠和 ROI
