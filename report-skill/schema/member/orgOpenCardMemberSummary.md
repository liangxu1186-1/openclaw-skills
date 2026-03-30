# 门店新增开卡会员排行

## 接口基本信息

- 原始路径 (path): `/report/scrm/member/orgOpenCardMemberSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内按门店聚合的新增开卡会员排行，返回每个门店的开卡会员数量。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId`、`userId`、`orgAuthList`、`memberCardSchemeAuthList`，服务端会根据 `X-OpenClaw-PublicKey` 自动补齐权限信息。
  服务端会强制把 `stime`、`etime` 从 8 位日期扩展为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  `dataNum` 不传时默认取 10，并直接作为分页 `pageSize` 使用。
  当返回项 `orgId = 0` 时，服务端会把 `orgName` 改写为 `线上自助`。
  若 `brandIdList` 过滤后没有可用卡方案，接口会返回空分页对象。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 头部门店的 `memberCount` 是否过度集中，用于判断新增会员获取是否依赖少数门店。
2. 若 `orgId = 0` 的线上自助占比较高，说明新增开卡更多来自线上渠道而非实体门店。
3. 可结合同时间段的储值排行、消费排行进一步看新增会员后续转化质量。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "门店新增开卡会员排行请求参数。原始路径: /report/scrm/member/orgOpenCardMemberSummary",
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
    "dataNum": {
      "type": ["integer", "null"],
      "description": "返回条数。不传默认 10，并直接作为分页大小。"
    },
    "pageNo": {
      "type": ["integer", "null"],
      "description": "页码。用于 PageHelper 分页。"
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
  "description": "门店新增开卡会员排行返回结果。该接口返回 BaseReportVo<MemberSummaryVo>。",
  "$defs": {
    "memberSummary": {
      "type": "object",
      "description": "单个门店的新增开卡会员排行项。",
      "properties": {
        "orgId": {
          "type": ["integer", "null"],
          "description": "开卡门店 ID。0 通常代表线上自助。"
        },
        "orgCode": {
          "type": ["string", "null"],
          "description": "开卡门店编码。"
        },
        "orgName": {
          "type": ["string", "null"],
          "description": "开卡门店名称。`orgId = 0` 时会被服务端改写为 `线上自助`。"
        },
        "transOrgId": {
          "type": ["integer", "null"],
          "description": "交易门店 ID。"
        },
        "transOrgCode": {
          "type": ["string", "null"],
          "description": "交易门店编码。"
        },
        "transOrgName": {
          "type": ["string", "null"],
          "description": "交易门店名称。"
        },
        "groupById": {
          "type": ["integer", "null"],
          "description": "当前分组 ID。"
        },
        "groupByCode": {
          "type": ["string", "null"],
          "description": "当前分组编码。"
        },
        "groupByName": {
          "type": ["string", "null"],
          "description": "当前分组名称。"
        },
        "memberCount": {
          "type": ["integer", "null"],
          "description": "新增开卡会员数量。"
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
        "$ref": "#/$defs/memberSummary"
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
  "dataNum": 10
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/scrm/member/orgOpenCardMemberSummary' '{"flag":2,"stime":20260301,"etime":20260307,"pageNo":1,"dataNum":10}'
```
