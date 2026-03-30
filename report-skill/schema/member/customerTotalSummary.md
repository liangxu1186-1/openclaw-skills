# 客户看板汇总统计

## 接口基本信息

- 原始路径 (path): `/report/scrm/member/customerTotalSummary`
- 请求方法: `POST`
- 功能描述:
  查询客户看板汇总统计，返回顾客规模、会员规模、累计储值、累计余额消费、沉淀金额与转化率等会员核心指标。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId`、`userId`、`orgAuthList`、`memberCardSchemeAuthList`，服务端会根据 `X-OpenClaw-PublicKey` 自动补齐权限信息。
  若 `brandIdList` 过滤后没有可用卡方案，接口会直接返回空对象。
  服务端内部会把本接口转成汇总版 `CustomerPeriodSummaryDto` 执行，因此部分统计口径与按范围接口共用同一套会员汇总逻辑。
  当集团命中服务端配置 `ignoreGroupIdList` 时，返回中的 `ignoreFiledList` 会标识需要前端忽略的字段，当前实现会写入 `totalSedimentaryAmount`、`totalRechargeAmount`。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. `customerCount`、`memberCount`、`consumeMemberCount` 的层级关系，可判断会员渗透与活跃水平。
2. `totalRechargeAmount`、`totalBalance`、`totalSedimentaryAmount`、`totalSedimentaryRate` 的组合，可判断储值沉淀压力。
3. `changeMemberRate`、`changeConsumeRate`、`changeRechargeRate`、`changeConsumeBalanceRate` 可反映从顾客到会员、从会员到储值、从储值到余额消费的转化效率。
4. 若 `ignoreFiledList` 非空，应提醒调用方不要展示这些字段，也不要据此输出经营结论。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "客户看板汇总统计请求参数。原始路径: /report/scrm/member/customerTotalSummary",
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
    "orgAuthList": {
      "type": ["array", "null"],
      "description": "权限门店列表。通常由服务端自动补齐，调用方无需主动传递。",
      "items": {
        "type": "integer"
      }
    },
    "memberCardSchemeAuthList": {
      "type": ["array", "null"],
      "description": "权限会员卡方案列表。通常由服务端自动补齐。",
      "items": {
        "type": "integer"
      }
    },
    "clientSource": {
      "type": ["string", "null"],
      "description": "客户端标识。"
    },
    "sortColumn": {
      "type": ["string", "null"],
      "description": "排序字段。当前接口主流程通常不依赖。"
    },
    "sort": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "排序方式。0-升序，1-降序。当前接口主流程通常不依赖。"
    },
    "forceRefresh": {
      "type": ["boolean", "null"],
      "description": "是否强制刷新缓存。默认 false。"
    },
    "isMemberAdb": {
      "type": ["integer", "null"],
      "description": "会员是否走 ADB 数据源。一般由服务端内部决定。"
    }
  }
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "客户看板汇总统计返回结果。该接口直接返回 CustomerSummaryVo，本身包含 success/code/message 等基础状态字段。",
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
      "description": "顾客数量。"
    },
    "consumeCustomerCount": {
      "type": ["integer", "null"],
      "description": "有消费顾客数。"
    },
    "cardCount": {
      "type": ["integer", "null"],
      "description": "会员卡数量。"
    },
    "memberCount": {
      "type": ["integer", "null"],
      "description": "会员数量。"
    },
    "consumeMemberCount": {
      "type": ["integer", "null"],
      "description": "有消费会员数。"
    },
    "totalRechargeAmount": {
      "type": ["number", "null"],
      "description": "累计储值总金额。"
    },
    "totalRechargeMoneyAmount": {
      "type": ["number", "null"],
      "description": "累计储值本金总金额。"
    },
    "totalRechargeGiveAmount": {
      "type": ["number", "null"],
      "description": "累计储值赠金总金额。"
    },
    "totalRechargeRefundAmount": {
      "type": ["number", "null"],
      "description": "累计储值退款总金额。"
    },
    "totalRechargeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "累计储值退款本金总金额。"
    },
    "totalRechargeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "累计储值退款赠金总金额。"
    },
    "totalBalance": {
      "type": ["number", "null"],
      "description": "储值余额。"
    },
    "totalGiveBalance": {
      "type": ["number", "null"],
      "description": "储值赠金余额。"
    },
    "totalMoneyBalance": {
      "type": ["number", "null"],
      "description": "储值本金余额。"
    },
    "rechargeMemberCount": {
      "type": ["integer", "null"],
      "description": "储值人数。"
    },
    "changeMemberRate": {
      "type": ["number", "null"],
      "description": "会员转换率。"
    },
    "changeConsumeRate": {
      "type": ["number", "null"],
      "description": "会员活跃度 / 消费转化率。"
    },
    "changeRechargeRate": {
      "type": ["number", "null"],
      "description": "储值转换率。"
    },
    "perRechargeAmount": {
      "type": ["number", "null"],
      "description": "人均储值金额。"
    },
    "fundSedimentRate": {
      "type": ["number", "null"],
      "description": "余额资金沉淀率。通常为储值余额 / 累计储值额。"
    },
    "consumeBalanceMemberCount": {
      "type": ["integer", "null"],
      "description": "有余额消费会员数量。"
    },
    "totalConsumeBalanceAmount": {
      "type": ["number", "null"],
      "description": "累计余额消费总金额。"
    },
    "totalConsumeMoneyBalanceAmount": {
      "type": ["number", "null"],
      "description": "累计余额消费本金总金额。"
    },
    "totalConsumeGiveBalanceAmount": {
      "type": ["number", "null"],
      "description": "累计余额消费赠金总金额。"
    },
    "totalConsumeRefundAmount": {
      "type": ["number", "null"],
      "description": "会员退款总金额。"
    },
    "totalConsumeRefundMoneyAmount": {
      "type": ["number", "null"],
      "description": "会员退款本金总金额。"
    },
    "totalConsumeRefundGiveAmount": {
      "type": ["number", "null"],
      "description": "会员退款赠金总金额。"
    },
    "changeConsumeBalanceRate": {
      "type": ["number", "null"],
      "description": "余额消费转换率。"
    },
    "totalSedimentaryAmount": {
      "type": ["number", "null"],
      "description": "累计沉淀金额。通常为累计储值额减累计余额消费额。"
    },
    "totalSedimentaryMoneyAmount": {
      "type": ["number", "null"],
      "description": "累计沉淀本金金额。"
    },
    "totalSedimentaryGiveAmount": {
      "type": ["number", "null"],
      "description": "累计沉淀赠金金额。"
    },
    "totalSedimentaryRate": {
      "type": ["number", "null"],
      "description": "累计沉淀率。"
    },
    "updateTime": {
      "type": ["string", "null"],
      "description": "更新时间。"
    },
    "ignoreFiledList": {
      "type": ["array", "null"],
      "description": "需要前端忽略的字段名列表。",
      "items": {
        "type": "string"
      }
    }
  }
}
```

请求体示例:

```json
{
  "orgId": 20001,
  "brandIdList": [3001],
  "isStudentMember": 0,
  "isNotContainsGiveMoney": 0
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/scrm/member/customerTotalSummary' '{"orgId":20001,"brandIdList":[3001],"isStudentMember":0,"isNotContainsGiveMoney":0}'
```
