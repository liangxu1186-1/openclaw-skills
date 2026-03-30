# 查询商品收入科目统计列表

## 接口基本信息

- 原始路径 (path): `/report/getOrderIncomeStatsList`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的商品收入科目统计列表，返回基础收入汇总、分页列表、合计行和按收入科目展开的动态表头。主列表按门店 / 城市 / 省份等分组展示流水金额、实收金额和优惠金额，并在动态 `map` 字段中展开不同收入科目下的金额与占比指标。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  当 `period` 为空时，服务端默认按 `1-日` 处理。
  当 `period = 2` 且 `stime` / `etime` 只传 6 位年月时，服务端会自动扩展为整月起止日期。
  当 `flag = 1` 且 `stime` / `etime` 只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  当 `metrics` 为空时，服务端默认查询：`orderAmount`、`orderAmountRate`、`actualReceiptAmount`、`actualReceiptAmountRate`、`discountAmount`、`discountAmountRate`。
  `dimensions` 字段在当前实现中不参与计算，可视为保留字段。
  返回体是 `HeaderReportVo<OrderIncomeStatsVo>`，其中 `headList` 和 `sum` 会随着收入科目和列配置动态变化。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 哪些收入科目贡献了最高的流水金额和实收金额，是否存在明显集中。
2. 哪些收入科目的优惠金额或优惠占比异常高，是否可能存在促销、折扣或口径问题。
3. 基础汇总与各收入科目拆分之间是否匹配，是否存在“未设置收入科目”或异常收入科目。
4. 不同门店 / 城市 / 省份下，收入科目结构是否明显不同。
5. 如果某个收入科目流水高但实收低，或优惠高于预期，应提示用户进一步核对商品归属和收入科目配置。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询商品收入科目统计列表请求参数。原始路径: /report/getOrderIncomeStatsList",
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
      "description": "开始时间。可传 8 位日期 yyyyMMdd；当 period=2 时也可传 6 位年月 yyyyMM。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。可传 8 位日期 yyyyMMdd；当 period=2 时也可传 6 位年月 yyyyMM。"
    },
    "period": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "统计周期。1-日，2-月，3-自定义，4-周。为空时默认 1。"
    },
    "groupKey": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "分组维度。1-门店，2-城市，3-省份；为空时通常只返回基础收入字段。"
    },
    "metrics": {
      "type": ["array", "null"],
      "description": "指标编码列表。不传时服务端会使用默认收入指标集合。",
      "items": {
        "type": "string",
        "enum": [
          "orderAmount",
          "orderAmountRate",
          "actualReceiptAmount",
          "actualReceiptAmountRate",
          "discountAmount",
          "discountAmountRate"
        ]
      }
    },
    "dimensions": {
      "type": ["integer", "null"],
      "description": "保留字段，当前实现中不使用。"
    },
    "pageNo": {
      "type": ["integer", "null"],
      "description": "页码。"
    },
    "pageSize": {
      "type": ["integer", "null"],
      "description": "每页条数。"
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
  "description": "商品收入科目统计列表返回结果。该接口直接返回 HeaderReportVo<OrderIncomeStatsVo>，本身包含 success/code/message 等基础状态字段。",
  "$defs": {
    "head": {
      "type": "object",
      "description": "动态表头节点。既可能是普通列，也可能是收入科目分组列。",
      "properties": {
        "title": {
          "type": ["string", "null"],
          "description": "列标题。"
        },
        "key": {
          "type": ["string", "null"],
          "description": "列字段 key。动态收入科目列通常形如 `收入科目ID_orderAmount`。"
        },
        "type": {
          "type": ["string", "null"],
          "description": "列类型，例如文本、数值、比例等。"
        },
        "precision": {
          "type": ["integer", "null"],
          "description": "数值精度。"
        },
        "sort": {
          "type": ["integer", "null"],
          "description": "排序字段。"
        },
        "width": {
          "type": ["integer", "null"],
          "description": "列宽。"
        },
        "children": {
          "type": ["array", "null"],
          "description": "子列列表；存在时表示这是一个收入科目分组表头。",
          "items": {
            "$ref": "#/$defs/head"
          }
        }
      }
    },
    "orderIncomeStats": {
      "type": "object",
      "description": "单条收入科目统计记录。",
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
        "cityId": {
          "type": ["string", "null"],
          "description": "城市 ID。"
        },
        "cityName": {
          "type": ["string", "null"],
          "description": "城市名称。"
        },
        "provinceId": {
          "type": ["string", "null"],
          "description": "省份 ID。"
        },
        "provinceName": {
          "type": ["string", "null"],
          "description": "省份名称。"
        },
        "periodDate": {
          "type": ["string", "null"],
          "description": "统计日期。当 period=1 或 2 时通常返回。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "流水金额。"
        },
        "orderAmountRate": {
          "type": ["string", "null"],
          "description": "流水金额占比。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实收金额。"
        },
        "actualReceiptAmountRate": {
          "type": ["string", "null"],
          "description": "实收金额占比。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额。"
        },
        "discountAmountRate": {
          "type": ["string", "null"],
          "description": "优惠占比。"
        },
        "map": {
          "type": ["object", "null"],
          "description": "动态收入科目指标集合。key 形如 `收入科目ID_指标编码`，例如 `3001_orderAmount`。科目未配置时可能出现 `0_xxx` 或负值 key。",
          "additionalProperties": {
            "type": ["number", "string", "integer", "null"]
          }
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
    "pageNo": {
      "type": ["integer", "null"],
      "description": "当前页码。"
    },
    "pageSize": {
      "type": ["integer", "null"],
      "description": "每页条数。"
    },
    "total": {
      "type": ["integer", "null"],
      "description": "总条数。"
    },
    "list": {
      "type": ["array", "null"],
      "description": "分页结果列表。",
      "items": {
        "$ref": "#/$defs/orderIncomeStats"
      }
    },
    "sum": {
      "$ref": "#/$defs/orderIncomeStats"
    },
    "headList": {
      "type": ["array", "null"],
      "description": "动态表头定义。固定列和按收入科目展开的动态列都会出现在这里。",
      "items": {
        "$ref": "#/$defs/head"
      }
    }
  }
}
```

请求体示例:

```json
{
  "groupKey": 1,
  "flag": 2,
  "stime": 20260301,
  "etime": 20260307,
  "pageNo": 1,
  "pageSize": 20,
  "metrics": [
    "orderAmount",
    "orderAmountRate",
    "actualReceiptAmount",
    "discountAmount"
  ]
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/getOrderIncomeStatsList' '{"groupKey":1,"flag":2,"stime":20260301,"etime":20260307,"pageNo":1,"pageSize":20,"metrics":["orderAmount","orderAmountRate","actualReceiptAmount","discountAmount"]}'
```
