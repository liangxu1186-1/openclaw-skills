# 客户看板按范围统计

## 接口基本信息

- 原始路径 (path): `/report/scrm/member/customerPeriodSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的客户看板统计，返回当前期、上期，以及部分同比口径下的会员规模、储值、余额消费、沉淀与会员订单指标。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId`、`userId`、`orgAuthList`、`memberCardSchemeAuthList`，服务端会根据 `X-OpenClaw-PublicKey` 自动补齐权限信息。
  服务端会强制把 `stime`、`etime` 从 8 位日期扩展为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  服务端会自动计算上期区间，并按配置项 `querySame` 决定是否计算同比；当同比关闭时，`sameConsumeCountRate`、`sameDisFrontOrderAverageRate`、`sameOrderNumRate` 会返回 `0`。
  服务端会补充 `startPt`、`endPt` 作为缓存与数仓查询边界，通常无需调用方传递。
  若 `brandIdList` 过滤后没有可用卡方案，接口会直接返回空对象。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. `chainCustomerRate`、`chainMemberRate`、`chainConsumeCountRate` 用于判断会员增长和活跃变化。
2. `chainRechargeAmountRate`、`chainTotalConsumeBalanceAmountRate`、`chainTotalSedimentaryAmountRate` 可反映储值和沉淀趋势。
3. `orderAmount`、`orderNum`、`disFrontDayAverage`、`disFrontOrderAverage` 与对应上期字段可用于判断会员消费质量。
4. `memberActualAmountRate`、`memberTotalAmountRate` 可帮助判断会员订单在全量订单中的贡献度。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "客户看板按范围统计请求参数。原始路径: /report/scrm/member/customerPeriodSummary",
  "properties": {
    "orgId": {
      "type": ["integer", "null"],
      "description": "组织 ID / 门店 ID。与 orgIdList 二选一或同时传递。"
    },
    "orgIdList": {
      "type": ["array", "null"],
      "description": "组织 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "flag": {
      "type": "integer",
      "enum": [1, 2, 3],
      "description": "日期标识。1-销售日，2-营业日，3-开台日。"
    },
    "stime": {
      "type": ["integer", "string"],
      "description": "开始日期，通常传 8 位 `yyyyMMdd`。服务端会自动补齐时分秒。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束日期，通常传 8 位 `yyyyMMdd`。服务端会自动补齐时分秒。"
    },
    "period": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "统计周期。1-日，2-月，3-自定义，4-周。用于推算上期区间。"
    },
    "groupKey": {
      "type": ["integer", "null"],
      "description": "统计维度。会员相关口径可见代码注释：1-门店，2-城市，3-省份，4-会员，5-日期，6-方案，7-等级，8-品牌。当前接口主结果为汇总指标，通常不依赖该字段。"
    },
    "dataNum": {
      "type": ["integer", "null"],
      "description": "数据条数。该接口主结果为汇总指标，通常不依赖该字段。"
    },
    "isStudentMember": {
      "type": ["integer", "null"],
      "description": "是否统计学生会员。0-否，1-是。"
    },
    "isNotContainsGiveMoney": {
      "type": ["integer", "null"],
      "description": "是否只统计本金，不含赠送金额。0-否，1-是。"
    },
    "cardSchemeIdList": {
      "type": ["array", "null"],
      "description": "卡方案 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "brandIdList": {
      "type": ["array", "null"],
      "description": "品牌 ID 列表。服务端会据此反查可用卡方案。",
      "items": {
        "type": "integer"
      }
    },
    "transTypeList": {
      "type": ["array", "null"],
      "description": "交易类型列表，主要用于区分储值退款。主流程通常可不传。",
      "items": {
        "type": "integer"
      }
    },
    "clientSource": {
      "type": ["string", "null"],
      "description": "客户端标识。"
    },
    "shiftStatus": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否交班。0-否，1-是。"
    },
    "isTest": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否查询测试单。0-否，1-是。"
    },
    "viewType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "trainingMode": {
      "type": ["integer", "null"],
      "description": "练习标识。0-正常，1-测试。"
    }
  },
  "required": ["flag", "stime", "etime"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "客户看板按范围统计返回结果。该接口直接返回 CustomerPeriodSummaryVo，本身包含 success/code/message 等基础状态字段。",
  "properties": {
    "success": {
      "type": ["boolean", "null"],
      "description": "是否成功。"
    },
    "code": {
      "type": ["string", "integer", "null"],
      "description": "状态码。"
    },
    "message": {
      "type": ["string", "null"],
      "description": "提示信息。"
    },
    "customerCount": {
      "type": ["integer", "null"],
      "description": "当前期顾客数。"
    },
    "consumeCustomerCount": {
      "type": ["integer", "null"],
      "description": "当前期有消费顾客数。"
    },
    "cardCount": {
      "type": ["integer", "null"],
      "description": "当前期会员卡数量。"
    },
    "memberCount": {
      "type": ["integer", "null"],
      "description": "当前期会员数。"
    },
    "consumeMemberCount": {
      "type": ["integer", "null"],
      "description": "当前期有消费会员数。"
    },
    "totalRechargeAmount": {
      "type": ["number", "null"],
      "description": "当前期储值总金额。"
    },
    "totalRechargeMoneyAmount": {
      "type": ["number", "null"],
      "description": "当前期储值本金总金额。"
    },
    "totalRechargeGiveAmount": {
      "type": ["number", "null"],
      "description": "当前期储值赠金总金额。"
    },
    "totalRechargeRefundAmount": {
      "type": ["number", "null"],
      "description": "当前期储值退款总金额。"
    },
    "totalRechargeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "当前期储值退款本金总金额。"
    },
    "totalRechargeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "当前期储值退款赠金总金额。"
    },
    "totalBalance": {
      "type": ["number", "null"],
      "description": "当前期储值余额。"
    },
    "totalGiveBalance": {
      "type": ["number", "null"],
      "description": "当前期储值赠金余额。"
    },
    "totalMoneyBalance": {
      "type": ["number", "null"],
      "description": "当前期储值本金余额。"
    },
    "rechargeMemberCount": {
      "type": ["integer", "null"],
      "description": "当前期储值人数。"
    },
    "changeMemberRate": {
      "type": ["number", "null"],
      "description": "当前期会员转换率。"
    },
    "consumeBalanceMemberCount": {
      "type": ["integer", "null"],
      "description": "当前期有余额消费会员数。"
    },
    "totalConsumeBalanceAmount": {
      "type": ["number", "null"],
      "description": "当前期余额消费总金额。"
    },
    "totalConsumeMoneyBalanceAmount": {
      "type": ["number", "null"],
      "description": "当前期余额消费本金总金额。"
    },
    "totalConsumeGiveBalanceAmount": {
      "type": ["number", "null"],
      "description": "当前期余额消费赠金总金额。"
    },
    "totalConsumeRefundAmount": {
      "type": ["number", "null"],
      "description": "当前期退款总金额。"
    },
    "totalConsumeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "当前期退款本金总金额。"
    },
    "totalConsumeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "当前期退款赠金总金额。"
    },
    "changeConsumeBalanceRate": {
      "type": ["number", "null"],
      "description": "当前期余额消费转换率。"
    },
    "perRechargeAmount": {
      "type": ["number", "null"],
      "description": "当前期人均储值金额。"
    },
    "fundSedimentRate": {
      "type": ["number", "null"],
      "description": "当前期余额资金沉淀率。"
    },
    "totalSedimentaryAmount": {
      "type": ["number", "null"],
      "description": "当前期沉淀金额。"
    },
    "totalSedimentaryMoneyAmount": {
      "type": ["number", "null"],
      "description": "当前期沉淀本金金额。"
    },
    "totalSedimentaryGiveAmount": {
      "type": ["number", "null"],
      "description": "当前期沉淀赠金金额。"
    },
    "totalSedimentaryRate": {
      "type": ["number", "null"],
      "description": "当前期沉淀率。"
    },
    "changeConsumeRate": {
      "type": ["number", "null"],
      "description": "当前期消费转化率。"
    },
    "changeRechargeRate": {
      "type": ["number", "null"],
      "description": "当前期储值转化率。"
    },
    "orderAmount": {
      "type": ["number", "null"],
      "description": "当前期会员订单金额。"
    },
    "orderNum": {
      "type": ["integer", "null"],
      "description": "当前期会员有效订单数。"
    },
    "disFrontDayAverage": {
      "type": ["number", "null"],
      "description": "当前期折前日均。"
    },
    "disFrontOrderAverage": {
      "type": ["number", "null"],
      "description": "当前期折前单均。"
    },
    "upCustomerCount": {
      "type": ["integer", "null"],
      "description": "上期顾客数。"
    },
    "upConsumeCustomerCount": {
      "type": ["integer", "null"],
      "description": "上期消费顾客数。"
    },
    "upCardCount": {
      "type": ["integer", "null"],
      "description": "上期会员卡数量。"
    },
    "upMemberCount": {
      "type": ["integer", "null"],
      "description": "上期会员数。"
    },
    "upConsumeMemberCount": {
      "type": ["integer", "null"],
      "description": "上期有消费会员数。"
    },
    "upTotalRechargeAmount": {
      "type": ["number", "null"],
      "description": "上期储值总金额。"
    },
    "upTotalRechargeMoneyAmount": {
      "type": ["number", "null"],
      "description": "上期储值本金总金额。"
    },
    "upTotalRechargeGiveAmount": {
      "type": ["number", "null"],
      "description": "上期储值赠金总金额。"
    },
    "upTotalRechargeRefundAmount": {
      "type": ["number", "null"],
      "description": "上期储值退款总金额。"
    },
    "upTotalRechargeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "上期储值退款本金总金额。"
    },
    "upTotalRechargeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "上期储值退款赠金总金额。"
    },
    "upRechargeMemberCount": {
      "type": ["integer", "null"],
      "description": "上期储值人数。"
    },
    "upConsumeBalanceMemberCount": {
      "type": ["integer", "null"],
      "description": "上期有余额消费会员数。"
    },
    "upTotalConsumeBalanceAmount": {
      "type": ["number", "null"],
      "description": "上期余额消费总金额。"
    },
    "upTotalConsumeMoneyBalanceAmount": {
      "type": ["number", "null"],
      "description": "上期余额消费本金总金额。"
    },
    "upTotalConsumeGiveBalanceAmount": {
      "type": ["number", "null"],
      "description": "上期余额消费赠金总金额。"
    },
    "upTotalConsumeRefundAmount": {
      "type": ["number", "null"],
      "description": "上期退款总金额。"
    },
    "upTotalConsumeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "上期退款本金总金额。"
    },
    "upTotalConsumeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "上期退款赠金总金额。"
    },
    "upTotalSedimentaryAmount": {
      "type": ["number", "null"],
      "description": "上期沉淀金额。"
    },
    "upTotalSedimentaryMoneyAmount": {
      "type": ["number", "null"],
      "description": "上期沉淀本金金额。"
    },
    "upTotalSedimentaryGiveAmount": {
      "type": ["number", "null"],
      "description": "上期沉淀赠金金额。"
    },
    "upTotalSedimentaryRate": {
      "type": ["number", "null"],
      "description": "上期沉淀率。"
    },
    "upChangeConsumeRate": {
      "type": ["number", "null"],
      "description": "上期消费转化率。"
    },
    "upChangeRechargeRate": {
      "type": ["number", "null"],
      "description": "上期储值转化率。"
    },
    "upOrderAmount": {
      "type": ["number", "null"],
      "description": "上期会员订单金额。"
    },
    "upOrderNum": {
      "type": ["integer", "null"],
      "description": "上期会员有效订单数。"
    },
    "upDisFrontDayAverage": {
      "type": ["number", "null"],
      "description": "上期折前日均。"
    },
    "upDisFrontOrderAverage": {
      "type": ["number", "null"],
      "description": "上期折前单均。"
    },
    "chainMemberRate": {
      "type": ["number", "null"],
      "description": "会员数环比。"
    },
    "chainCustomerRate": {
      "type": ["number", "null"],
      "description": "顾客数环比。"
    },
    "chainCardRate": {
      "type": ["number", "null"],
      "description": "会员卡数环比。"
    },
    "chainConsumeCountRate": {
      "type": ["number", "null"],
      "description": "消费会员数环比。"
    },
    "chainConsumeRefundAmountRate": {
      "type": ["number", "null"],
      "description": "退款金额环比。"
    },
    "chainRechargeAmountRate": {
      "type": ["number", "null"],
      "description": "储值金额环比。"
    },
    "chainRechargeMoneyAmountRate": {
      "type": ["number", "null"],
      "description": "储值本金环比。"
    },
    "chainRechargeGiveAmountRate": {
      "type": ["number", "null"],
      "description": "储值赠金环比。"
    },
    "chainRechargeRefundAmountRate": {
      "type": ["number", "null"],
      "description": "储值退款金额环比。"
    },
    "chainRechargeCountRate": {
      "type": ["number", "null"],
      "description": "储值人数环比。"
    },
    "chainDisFrontDayAverageRate": {
      "type": ["number", "null"],
      "description": "折前日均环比。"
    },
    "chainDisFrontOrderAverageRate": {
      "type": ["number", "null"],
      "description": "折前单均环比。"
    },
    "chainOrderNumRate": {
      "type": ["number", "null"],
      "description": "会员订单数环比。"
    },
    "memberActualAmount": {
      "type": ["number", "null"],
      "description": "当前期会员实收金额。"
    },
    "memberTotalAmount": {
      "type": ["number", "null"],
      "description": "当前期会员流水金额。"
    },
    "memberActualAmountRate": {
      "type": ["number", "null"],
      "description": "会员实收占比。"
    },
    "memberTotalAmountRate": {
      "type": ["number", "null"],
      "description": "会员流水占比。"
    },
    "chainTotalConsumeBalanceAmountRate": {
      "type": ["number", "null"],
      "description": "余额消费总金额环比。"
    },
    "chainTotalConsumeMoneyBalanceAmountRate": {
      "type": ["number", "null"],
      "description": "余额消费本金环比。"
    },
    "chainTotalConsumeGiveBalanceAmountRate": {
      "type": ["number", "null"],
      "description": "余额消费赠金环比。"
    },
    "chainTotalSedimentaryAmountRate": {
      "type": ["number", "null"],
      "description": "沉淀金额环比。"
    },
    "chainTotalSedimentaryRateRate": {
      "type": ["number", "null"],
      "description": "沉淀率环比差值。"
    },
    "chainChangeConsumeRateRate": {
      "type": ["number", "null"],
      "description": "消费转化率环比差值。"
    },
    "chainChangeRechargeRateRate": {
      "type": ["number", "null"],
      "description": "储值转化率环比差值。"
    },
    "sameConsumeCountRate": {
      "type": ["number", "null"],
      "description": "消费会员数同比。服务端关闭同比时返回 0。"
    },
    "sameDisFrontOrderAverageRate": {
      "type": ["number", "null"],
      "description": "折前单均同比。服务端关闭同比时返回 0。"
    },
    "sameOrderNumRate": {
      "type": ["number", "null"],
      "description": "会员订单数同比。服务端关闭同比时返回 0。"
    },
    "updateTime": {
      "type": ["string", "null"],
      "description": "更新时间。"
    }
  }
}
```

请求体示例:

```json
{
  "orgId": 20001,
  "flag": 2,
  "stime": 20260301,
  "etime": 20260307,
  "period": 3,
  "isStudentMember": 0,
  "isNotContainsGiveMoney": 0
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/scrm/member/customerPeriodSummary' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"period":3,"isStudentMember":0,"isNotContainsGiveMoney":0}'
```
