---
name: report-skill
description: 当用户要查询经营总览、门店榜单、会员偏好等报表，并且应通过统一的 /agent/... 接口完成查询时使用。
---

通过 `scripts/report_proxy.py` 调用统一的 agent 报表接口。

当前 skill 只面向 `report-skill` 自己登记的 `/agent/...` 路径，不再理解旧的 `/report/...` 接口、旧参数族或 legacy schema。

## 硬约束
1. 所有请求都必须通过 `./scripts/report_proxy.py` 发起。
2. 只允许调用当前 skill 已登记的 `/agent/...` 接口。
3. 请求参数统一使用 `startTime`、`endTime`、`flag`；未传 `flag` 时默认按 `2=营业日` 处理。
4. 所有查询时间范围都不能超过 `90` 天。
5. 成功时接口直接返回业务 JSON；错误时返回错误 JSON。
6. 不要在 skill 层补 legacy 报表参数，不要手写 bridge 前缀。
7. 线上请求参数名保持 `publicKey` 不变，但其值只允许来自四处：优先读取环境变量 `OPENCLAW_IDENTITY`；云端单用户场景下，其次读取 `/home/gem/workspace/agent/openclaw.json` 中 `channels.feishu.appId + allowFrom[0]`，并规范成 `feishu-owner:{appId}:{openId}`；否则读取 `~/.openclaw/identity/device.json` 中的 `deviceId`；最后兜底读取 `/home/gem/workspace/agent/identity/device.json`；不要再从其他路径推导或兜底。
8. 当前已登记的接口分为两类：
   - 已实现：可以正常用于查询和回答
   - 已定义待实现：当前明确返回 `NOT_IMPLEMENTED`，用于接口联调，不要把它误当成稳定生产能力

## 当前接口
| 业务域 | 用户意图 | 接口路径 | 状态 |
| --- | --- | --- | --- |
| 订单 | 今日营业额 / 本月营业额 / 实收 / 优惠 / 客流 / 订单数 | `/agent/order/overview` | 已实现 |
| 订单 | 门店榜单 / 门店排行 | `/agent/order/shop-ranking` | 已实现 |
| 订单 | 订单业务类型分组 | `/agent/order/business-type` | 已实现 |
| 订单 | 订单渠道类型分组 | `/agent/order/channel-type` | 已实现 |
| 订单 | 订单退款数据 | `/agent/order/refund` | 已实现 |
| 订单 | 订单餐段数据 | `/agent/order/meal-period` | 已实现 |
| 订单 | 订单时段数据 | `/agent/order/time-period` | 已实现 |
| 订单 | 收银员收款统计 | `/agent/order/cashier-income` | 已实现 |
| 商品 | 商品销售金额总览 | `/agent/goods/overview` | 已实现 |
| 商品 | 商品销售排行 | `/agent/goods/sales-ranking` | 已实现 |
| 商品 | 销售分类排行 | `/agent/goods/category-ranking` | 已实现 |
| 商品 | 商品退货排行 | `/agent/goods/refund-ranking` | 已实现 |
| 商品 | 商品赠送排行 | `/agent/goods/gift-ranking` | 已实现 |
| 商品 | 商品收入科目统计 / 收入科目构成 | `/agent/goods/income-subject` | 已实现 |
| 支付 | 支付构成 / 支付类目和科目明细 | `/agent/payment/compose` | 已实现 |
| 支付 | 支付优惠数据 | `/agent/payment/discount-overview` | 已定义待实现 |
| 营销 | 促销活动汇总 / 促销活动看板 | `/agent/marketing/promotion-summary` | 已实现 |
| 营销 | 营销活动汇总 / 营销活动看板 | `/agent/marketing/activity-summary` | 已实现 |
| 会员 | 会员总览 | `/agent/member/overview` | 已实现 |
| 会员 | 会员喜好商品 / 会员消费门店 / 会员消费门店排行 / 会员口味偏好 | `/agent/member/preference` | 已实现 |

## 执行规则
1. 命中上表中的已实现接口时，直接发起调用，不要再读取 legacy `api/*.md` 或 `schema/*.md`。
2. 时间范围明确时，先换算成绝对日期再调用。
3. 若时间范围超过 `90` 天，必须先要求用户缩小范围，不要发起调用。
4. `flag` 继续沿用现有业务定义；若用户未指定，默认传 `2=营业日`。
5. 返回成功 JSON 后，直接基于字段分析，不要求后端预组装自然语言。
6. `/agent/member/preference` 返回三块：`favoriteGoods`、`favoriteStores`、`favoritePractices`，回答时按这三块拆开。
7. “会员消费门店排行”走 `/agent/member/preference`，基于 `favoriteStores` 回答，不要再尝试调用独立的 `member/ranking`。
8. 若接口状态是“已定义待实现”，可以用于联调，但必须接受它当前会明确返回 `NOT_IMPLEMENTED`。
9. 若用户请求的能力尚未在当前接口表中出现，应明确说明“当前新 skill 尚未接入该 agent 接口”，不要退回旧 `/report/...`。

## 回答规则
1. `order/overview` 重点围绕 `orderAmount`、`incUnPayOrderAmount`、`unPayOrderAmount`、`unLdTotalAmount`、`actualReceiptAmount`、`discountAmount`、`discountRate`、`refundActualAmount`、`refundAmount`、`saleOrderNum`、`orderCount`、`refundOrderNum`、`refundOrderCount`、`customerNum`、`customerCount` 回答。
2. `order/shop-ranking` 重点围绕 `topStores` 回答；如果要说榜首门店，只看 `topStores[0]`。
3. `goods/income-subject` 优先围绕 `items` 里的 `incomeSubjectName`、`orderAmount`、`actualReceiptAmount`、`discountAmount` 回答。
4. `member/preference` 必须区分商品、门店、口味三块数据，不要把其中一块为空误说成“整体无数据”。
5. 如果用户问“会员消费门店排行”，优先围绕 `favoriteStores` 的 `shopName` 和 `amount` 作答。
6. `payment/compose` 先看顶层汇总，再看 `groupVoList`，最后看 `subjectVoList`。
7. `marketing/promotion-summary` 只看外层汇总字段，不要假设存在趋势 `dayList`。
8. `marketing/activity-summary` 直接基于原始业务字段回答，不要在 skill 层补推导指标。
9. 错误 JSON 表示调用失败，不等于空数据；不要把错误结果改写成“当前无数据”。
10. 默认只输出“结论 + 2 到 3 条关键要点”；不要展开成长段分析。
11. 没有明确要求时，不主动输出“可能原因”“优化建议”“排查建议”。
12. 没有明确要求时，不主动追问“是否继续看上月/别的报表/经营总览”。
13. 会员偏好类问题默认最多按“商品 / 门店 / 口味”三块各用一句话概括；不写多层列表。

## 调用示例
```bash
python3 ./scripts/report_proxy.py /agent/order/overview '{"startTime":20260401,"endTime":20260430,"flag":2}'
python3 ./scripts/report_proxy.py /agent/order/shop-ranking '{"startTime":20260401,"endTime":20260430,"flag":2}'
python3 ./scripts/report_proxy.py /agent/member/preference '{"startTime":20260401,"endTime":20260430,"flag":2}'
python3 ./scripts/report_proxy.py /agent/goods/overview '{"startTime":20260401,"endTime":20260430,"flag":2}'
python3 ./scripts/report_proxy.py /agent/payment/compose '{"startTime":20260401,"endTime":20260430,"flag":2}'
python3 ./scripts/report_proxy.py /agent/marketing/promotion-summary '{"startTime":20260401,"endTime":20260430,"flag":2}'
```

## 文档入口
1. 当前可用接口总览看 `./api/agent.md`
2. 订单域接口看 `./api/order.md`
3. 商品域接口看 `./api/goods.md`
4. 支付域接口看 `./api/payment.md`
5. 营销域接口看 `./api/marketing.md`
6. 会员域接口看 `./api/member.md`
7. 字段细节看 `./schema/agent/*.md`
8. 路径白名单和参数契约以 `./scripts/route_catalog.py` 为准
