---
name: report-analytics
description: 当用户想查今天营业额、实收金额、优惠金额、客流、订单数、退货金额，或查询商品分类销售排行、销售日报、订单经营汇总等经营分析数据时使用；适合处理“查询今天营业额”“看某门店商品分类销售排行”“查销售日报”等请求。
---

## 功能
通过 Python 代理脚本调用 SaaS 报表服务接口，支持营业指标、商品销售分析和订单经营日报类查询。

## 架构约束
1. 所有请求都必须通过 `./scripts/report_proxy.py` 发起。
2. 脚本必须自动为原始业务路径拼接 `/report/openclaw/bridge` 前缀。
3. 脚本必须通过 Header `X-OpenClaw-PublicKey` 注入 OpenClaw 本机设备公钥。优先读取环境变量 `OPENCLAW_PUBLIC_KEY`，未配置时自动从本机 OpenClaw 状态目录推导。
4. 接口文档和 schema 中必须始终使用原始业务路径，不带 bridge 前缀。
5. 不要假设固定的本机绝对路径。优先使用 `{baseDir}/scripts/report_proxy.py`，或从当前 skill 目录下的 `./scripts/report_proxy.py` 调用。
6. 支持通过环境变量 `SAAS_API_URL` 覆盖目标 SaaS 基础地址；未覆盖时使用脚本内置默认值。

## 脚本
1. `./scripts/report_proxy.py`

   功能:
   调用 SaaS 报表服务接口时，自动拼接 bridge 路径并注入 OpenClaw 公钥，默认优先返回面向问答的精简 JSON，而不是完整大表。

   命令行参数:
   - `path`: 原始业务路径，例如 `/report/getYzsBusinessMetrics`
   - `payload`: 请求体 JSON 字符串
   - `--method`: HTTP 方法，默认 `POST`
   - `--query`: URL 查询参数 JSON 字符串，可选
   - `--timeout`: 超时时间，单位秒，默认 `10`

   返回结果:
   - 成功时，打印裁剪后的结构化 JSON
   - 失败时，直接抛出错误，不自动重试

   示例:
   ```bash
   python3 ./scripts/report_proxy.py '/report/getYzsBusinessMetrics' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"period":3,"viewType":1}'
   ```

## 分析要求
1. 调用报表接口后，不要只复述返回字段，要结合脚本返回的摘要数据给出简短经营分析。
2. 分析表达可以自由组织，不要求固定段落、固定标题或固定模板。
3. 分析必须基于返回数据本身，不能编造接口中不存在的事实。
4. 如果某个判断属于推测，必须使用“可能”“疑似”“建议进一步确认”等表述。
5. 当数据没有明显特征时，可以只做简短总结，不强行分析。
6. 如果存在异常值、测试数据、临时分类、极端折扣、金额倒挂或字段之间明显不协调，应优先提醒用户关注。
7. 如果脚本已经返回 `summary`、`sum`、`topRows`、`topStores` 这类精简结构，就直接基于这些字段回答，不要为了“看全量数据”再次探测其他接口或要求重取完整大表，除非用户明确要求看明细。

## 易混接口速查
1. 先选对接口，再组参数；不要把一个接口的日期参数格式直接复用到另一个接口。
2. 常见易混接口快速对照：

   | 我想查什么 | 接口路径 | 正确关键参数 | 严禁误用 |
   | --- | --- | --- | --- |
   | 营业额 / 营业指标 | `/report/getYzsBusinessMetrics` | `flag`, `stime`, `etime`, `period`, `viewType` | 不要误写成 `dateType`, `startDate`, `endDate` |
   | 商品分类销售排行 | `/report/goodsPosCateSaleSummary` | `dateType`, `startDate`, `endDate`, `viewType` | 不要误写成 `flag`, `stime`, `etime`, `period` |
   | 门店榜单 / 门店排行 | `/report/getOrderShopRanking` | `metricsType`, `flag`, `stime`, `etime` | 不要误写成 `/report/getShopSaleRank`、`/report/shopRank`，也不要误用 `dateType`, `startDate`, `endDate`, `viewType` |
3. 如果用户问的是“商品销售情况”“商品分类销售排行”“销售分类排行”，默认优先检查 `goodsPosCateSaleSummary` 的参数格式，先想 `dateType/startDate/endDate/viewType`，不要沿用营业指标接口的 `flag/stime/etime/period`。
4. 如果用户问的是营业额、实收、优惠、客流、订单数等营业指标，才使用 `getYzsBusinessMetrics` 的 `flag/stime/etime/period` 这一套。
5. 如果用户问的是“门店榜单”“门店排行”“店铺排行”，默认优先检查 `getOrderShopRanking` 的参数格式，先想 `metricsType/flag/stime/etime`，不要沿用商品分类排行的 `dateType/startDate/endDate/viewType`，也不要臆造别名路径。

## 快速命中规则
1. 如果用户问题已经能落到下列意图，先直接执行脚本，不要先 `memory_search`，也不要先 `find`、`ls` 探测脚本位置：
   - “目前总共有多少会员” -> `/report/scrm/member/customerTotalSummary`
   - “这个月新增了多少会员” “上月新增了多少会员” “今日新增会员” -> `/report/scrm/member/customerPeriodSummary`
   - “上周新增的会员人数” “本周新增会员” “查询会员人数变化” -> 先看 `api/member.md`，优先使用 `/report/scrm/member/customerPeriodSummary`
   - “门店榜单” “门店排行” “店铺排行” -> `/report/getOrderShopRanking`
   - “支付科目” “支付分组” -> `/report/getPaymentGroupCompose`
   - “按业务类型查一下” -> `/report/orderBusinessDaily`
   - “商品销售情况” “商品分类销售排行” -> `/report/goodsPosCateSaleSummary`
2. 命中上述意图时，优先使用绝对脚本路径：
   ```bash
   python3 {baseDir}/scripts/report_proxy.py '原始路径' 'JSON请求体'
   ```
3. 如果接口返回体很大，不要逐段复述原始 JSON；只抽取回答当前问题所需的字段，再给结论。
4. 如果脚本已经返回裁剪后的结构化结果，优先直接总结；不要继续追 `headList`、超长 `list`、嵌套明细数组，也不要继续读更多 schema 文件。
5. 如果查询的是“这个月”“上月”这类明确时间范围，直接换算出绝对日期并执行，不要先让用户补日期。
6. 会员人数/会员新增类问题，不要猜测 `/report/memberAddSummary`、`/report/memberAnalysis` 这类未在 skill 中确认过的路径；优先使用 `customerTotalSummary` 或 `customerPeriodSummary` 这两条已确认路径和各自固定参数格式。
7. 当用户问“新增会员”“本月新增会员”“今日新增会员”时，只能使用 `/report/scrm/member/customerPeriodSummary`。该接口裁剪结果中的 `current.newMemberCount`、`current.newCardCount` 是本期新增口径，不能用 `customerTotalSummary` 的累计 `memberCount/cardCount` 替代回答。
8. 当用户问“门店榜单”“门店排行”但没有说明看什么指标时，默认按营业额榜单处理，即 `/report/getOrderShopRanking` + `metricsType=1`。如果用户明确说实收、客流、订单量，再切换对应 `metricsType`。
9. 对门店榜单问题，禁止猜测 `/report/getShopSaleRank`、`/report/shopRank` 这类未确认路径；也不要使用 `dateType/startDate/endDate/viewType` 这一套参数。
10. 用户没有明确要求“按平台拆开”“按业务类型拆开”“看完整列表”“看全部明细”时，不要主动追求完整大返回；默认把脚本输出的 summary 视为主回答依据。

## 接口说明
1. 营业指标相关数据，查看 [api/business.md](./api/business.md)
2. 商品销售分析相关数据，查看 [api/goods.md](./api/goods.md)
3. 订单经营分析相关数据，查看 [api/order.md](./api/order.md)
4. 会员报表相关数据，查看 [api/member.md](./api/member.md)
