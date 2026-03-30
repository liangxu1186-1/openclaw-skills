# 门店储值排行

## 接口基本信息

- 原始路径 (path): `/report/scrm/member/orgRechargeMemberSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的门店储值排行，返回按门店聚合的储值人数、储值总金额、本金和赠金金额。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId`、`userId`、`orgAuthList`、`memberCardSchemeAuthList`，服务端会根据 `X-OpenClaw-PublicKey` 自动补齐权限信息。
  服务端会强制把 `stime`、`etime` 从 8 位日期扩展为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  服务端会固定把 `pageSize` 设为 `10`，即使请求体里传了其他值也不会生效。
  `groupKey` 不传时，服务端默认写成 `1`。
  当返回项 `orgId = 0` 时，服务端会把 `orgName` 改写为 `线上自助`。
  若 `brandIdList` 过滤后没有可用卡方案，接口会返回空分页对象。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 对比 `rechargeMemberCount` 和 `totalRechargeAmount`，识别是高客单储值还是高人数储值驱动。
2. 观察 `totalRechargeMoneyAmount` 与 `totalRechargeGiveAmount` 的比例，判断储值活动赠金力度是否偏高。
3. 若线上自助门店进入前列，说明会员储值正在向线上化迁移。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "门店储值排行请求参数。原始路径: /report/scrm/member/orgRechargeMemberSummary",
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
      "description": "统计周期。可选。"
    },
    "groupKey": {
      "type": ["integer", "null"],
      "description": "统计维度。不传时服务端默认填 1。"
    },
    "pageNo": {
      "type": ["integer", "null"],
      "description": "页码。"
    },
    "pageSize": {
      "type": ["integer", "null"],
      "description": "每页条数。服务端会固定改写成 10。"
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
  "description": "门店储值排行返回结果。该接口返回 BaseReportVo<RechargeSummaryVo>。",
  "$defs": {
    "rechargeSummary": {
      "type": "object",
      "description": "单个门店的储值排行项。",
      "properties": {
        "orgId": {
          "type": ["integer", "null"],
          "description": "门店 ID。0 通常代表线上自助。"
        },
        "orgCode": {
          "type": ["string", "null"],
          "description": "门店编码。"
        },
        "orgName": {
          "type": ["string", "null"],
          "description": "门店名称。`orgId = 0` 时会被服务端改写为 `线上自助`。"
        },
        "transDate": {
          "type": ["string", "null"],
          "description": "交易日期。具体粒度取决于底层查询。"
        },
        "customerId": {
          "type": ["integer", "null"],
          "description": "客户 ID。当前门店排行主场景下通常可忽略。"
        },
        "customerName": {
          "type": ["string", "null"],
          "description": "客户名称。当前门店排行主场景下通常可忽略。"
        },
        "cardNo": {
          "type": ["string", "null"],
          "description": "卡号。当前门店排行主场景下通常可忽略。"
        },
        "rechargeMemberCount": {
          "type": ["integer", "null"],
          "description": "储值人数。"
        },
        "totalRechargeAmount": {
          "type": ["number", "null"],
          "description": "储值总金额。"
        },
        "totalRechargeMoneyAmount": {
          "type": ["number", "null"],
          "description": "储值本金金额。"
        },
        "totalRechargeGiveAmount": {
          "type": ["number", "null"],
          "description": "储值赠金金额。"
        },
        "updateTime": {
          "type": ["string", "null"],
          "description": "更新时间。"
        }
      }
    }
  },
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
    "size": {
      "type": ["integer", "null"],
      "description": "总条数。服务端使用 PageHelper 的 total 回填。"
    },
    "list": {
      "type": ["array", "null"],
      "description": "排行结果列表。",
      "items": {
        "$ref": "#/$defs/rechargeSummary"
      }
    }
  }
}
```

请求体示例:

```json
{
  "flag": 2,
  "stime": 20260301,
  "etime": 20260307,
  "pageNo": 1,
  "groupKey": 1
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/scrm/member/orgRechargeMemberSummary' '{"flag":2,"stime":20260301,"etime":20260307,"pageNo":1,"groupKey":1}'
```
