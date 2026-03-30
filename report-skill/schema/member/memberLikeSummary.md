# 会员喜好商品 / 口味统计

## 接口基本信息

- 原始路径 (path): `/report/memberLikeSummary`
- 请求方法: `POST`
- 功能描述:
  查询会员群体或单个会员在指定时间范围内的喜好商品、喜好做法，以及消费门店分布。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  当 `customerId` 为空时，接口按会员群体统计，并由服务端自动补齐权限信息；当 `customerId` 非空时，接口按单个会员统计。
  `summaryGoodsType` 必填，且只允许 `1` 或 `2`。1-套餐头，2-套餐明细。
  当 `flag = 1` 时，服务端会把 `stime`、`etime` 从 8 位日期扩展为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  `dataNum` 为空或为 `0` 时，服务端实际默认值是 `10`。
  服务端会自动补充 `startPt`、`endPt`，并可能根据配置覆盖 `excludeGoodsIdList`。
  当 `groupKey` 为空且走群体统计时，服务端会默认按门店维度查询消费门店排行。
  单会员模式下，`orgVoList` 是根据会员历史订单去重后的门店列表，不包含门店销售额。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. `goodsVoList` 可用于识别会员偏好的主力商品或套餐结构。
2. `practiceVoList` 适合判断会员的口味偏好、加料偏好和做法倾向。
3. 群体模式下 `orgVoList.orderAmount` 可反映会员消费集中门店；个人模式下则更适合看到访门店覆盖面。
4. 若返回为空，应优先检查时间范围、卡方案过滤、以及服务端排除商品配置是否命中。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "会员喜好商品 / 口味统计请求参数。原始路径: /report/memberLikeSummary",
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
      "description": "开始时间。通常传 8 位 `yyyyMMdd`；当 `flag = 1` 时服务端会自动补齐时分秒。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位 `yyyyMMdd`；当 `flag = 1` 时服务端会自动补齐时分秒。"
    },
    "period": {
      "type": ["integer", "null"],
      "description": "统计周期。可选。"
    },
    "groupKey": {
      "type": ["integer", "null"],
      "description": "分组维度。群体模式下为空时，服务端默认转成门店维度。"
    },
    "summaryGoodsType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "统计商品类型。1-套餐头，2-套餐明细。"
    },
    "customerId": {
      "type": ["string", "null"],
      "description": "会员 ID。传值时走单会员模式，不传时走会员群体模式。"
    },
    "customerIdList": {
      "type": ["array", "null"],
      "description": "会员 ID 列表。主要用于更细粒度会员集合过滤。",
      "items": {
        "type": "string"
      }
    },
    "dataNum": {
      "type": ["integer", "null"],
      "description": "返回条数。为空或为 0 时服务端默认 10。"
    },
    "isStudentMember": {
      "type": ["integer", "null"],
      "description": "是否统计学生会员。0-否，1-是。"
    },
    "excludeGoodsIdList": {
      "type": ["array", "null"],
      "description": "排除商品 ID 列表。服务端可能根据配置覆盖该字段。",
      "items": {
        "type": "integer"
      }
    },
    "orderNos": {
      "type": ["array", "null"],
      "description": "订单号列表。单会员模式下通常由服务端内部回填，调用方无需主动传递。",
      "items": {
        "type": "string"
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
  "required": ["flag", "stime", "etime", "summaryGoodsType"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "会员喜好商品 / 口味统计返回结果。该接口直接返回 MemberLikeSummaryVo，本身包含 success/code/message 等基础状态字段。",
  "$defs": {
    "goodsItem": {
      "type": "object",
      "description": "喜好商品项。",
      "properties": {
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。"
        },
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。"
        },
        "goodsCode": {
          "type": ["string", "null"],
          "description": "商品编码。"
        },
        "goodsNum": {
          "type": ["number", "null"],
          "description": "商品数量。"
        }
      }
    },
    "practiceItem": {
      "type": "object",
      "description": "喜好做法项。",
      "properties": {
        "practice": {
          "type": ["string", "null"],
          "description": "做法名称。"
        },
        "practiceNum": {
          "type": ["number", "null"],
          "description": "做法数量。"
        }
      }
    },
    "orgItem": {
      "type": "object",
      "description": "消费门店项。",
      "properties": {
        "orderAmount": {
          "type": ["number", "null"],
          "description": "消费金额。群体模式下通常有值，个人模式下通常为空。"
        },
        "orgId": {
          "type": ["integer", "null"],
          "description": "门店 ID。"
        },
        "orgCode": {
          "type": ["string", "null"],
          "description": "门店编码。"
        },
        "orgName": {
          "type": ["string", "null"],
          "description": "门店名称。"
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
          "description": "分组 ID。"
        },
        "groupByCode": {
          "type": ["string", "null"],
          "description": "分组编码。"
        },
        "groupByName": {
          "type": ["string", "null"],
          "description": "分组名称。"
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
    "goodsVoList": {
      "type": ["array", "null"],
      "description": "喜好商品列表。",
      "items": {
        "$ref": "#/$defs/goodsItem"
      }
    },
    "practiceVoList": {
      "type": ["array", "null"],
      "description": "喜好做法列表。",
      "items": {
        "$ref": "#/$defs/practiceItem"
      }
    },
    "orgVoList": {
      "type": ["array", "null"],
      "description": "消费门店列表。",
      "items": {
        "$ref": "#/$defs/orgItem"
      }
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
  "etime": 20260331,
  "summaryGoodsType": 1,
  "dataNum": 10
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/memberLikeSummary' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260331,"summaryGoodsType":1,"dataNum":10}'
```
