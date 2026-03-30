# 查询订单业务类型 / 订单渠道统计列表

## 接口基本信息

- 原始路径 (path): `/report/getOrderDimensionStatsList`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的订单业务类型或订单渠道统计列表，返回分页数据、合计行和动态表头。主列表按门店 / 城市 / 省份等分组展示基础经营指标，并在动态 `map` 字段中展开不同业务类型或渠道下的指标明细。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  `dimensions` 为必填：`1-业务类型`，`2-订单渠道`。
  当 `period` 为空时，服务端默认按 `1-日` 处理。
  当 `period = 2` 时，服务端会自动把 `stime` 和 `etime` 扩展为整月范围；若结束月份是当前月，则结束时间自动截到今天。
  当 `flag = 1` 且 `stime` / `etime` 只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  当 `metrics` 为空时，服务端默认查询：`orderAmount`、`actualReceiptAmount`、`discountAmount`、`discountAmountRate`、`saleOrderNum`、`disFrontOrderAverage`、`disAfterOrderAverage`、`customerNum`、`disBeforePersonAvg`、`disAfterPersonAvg`。
  返回体是 `HeaderReportVo<OrderDimensionStatsVo>`，其中 `headList` 和 `sum` 会跟随 `metrics`、`dimensions`、`groupKey` 动态变化。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 业务类型或渠道之间的收入、订单量、客流结构是否高度集中。
2. 哪个维度的折前 / 折后单均、人均明显偏高或偏低，是否存在经营结构差异。
3. 优惠金额与优惠占比在不同业务类型或渠道之间是否异常失衡。
4. 同一门店 / 城市 / 省份下，不同业务类型或渠道的动态指标差异是否明显。
5. 如果某些维度的订单量不高但金额异常高，或客流高但实收偏低，应优先提醒用户进一步核对。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询订单业务类型 / 订单渠道统计列表请求参数。原始路径: /report/getOrderDimensionStatsList",
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
      "description": "开始时间。通常传 8 位日期 yyyyMMdd；当 flag=1 时服务端会自动补齐时分秒。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd；当 flag=1 时服务端会自动补齐时分秒。"
    },
    "period": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "统计周期。1-日，2-月，3-自定义，4-周。为空时默认 1。"
    },
    "groupKey": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "分组维度。1-门店，2-城市，3-省份；为空时按门店粒度返回基础字段。"
    },
    "dimensions": {
      "type": "integer",
      "enum": [1, 2],
      "description": "统计维度。1-业务类型，2-订单渠道。"
    },
    "metrics": {
      "type": ["array", "null"],
      "description": "指标编码列表。不传时服务端会使用默认指标集合。",
      "items": {
        "type": "string",
        "enum": [
          "orderAmount",
          "incUnPayOrderAmount",
          "actualReceiptAmount",
          "discountAmount",
          "discountAmountRate",
          "saleOrderNum",
          "disFrontOrderAverage",
          "disAfterOrderAverage",
          "customerNum",
          "disBeforePersonAvg",
          "disAfterPersonAvg"
        ]
      }
    },
    "orderTypeList": {
      "type": ["array", "null"],
      "description": "订单类型列表。",
      "items": {
        "type": "string"
      }
    },
    "cashier": {
      "type": ["string", "null"],
      "description": "收银员条件，支持 id / 名称模糊匹配。"
    },
    "sortCode": {
      "type": ["integer", "null"],
      "description": "排序编码。服务端会根据该值换算成具体排序字段。"
    },
    "sortField": {
      "type": ["string", "null"],
      "description": "排序字段。通常由服务端根据 sortCode 自动设置。"
    },
    "isLimit": {
      "type": ["integer", "null"],
      "description": "是否限制返回条数。默认 1。"
    },
    "provinceIdList": {
      "type": ["array", "null"],
      "description": "省份 ID 列表。",
      "items": {
        "type": "string"
      }
    },
    "cityIdList": {
      "type": ["array", "null"],
      "description": "城市 ID 列表。",
      "items": {
        "type": "string"
      }
    },
    "pageNo": {
      "type": ["integer", "null"],
      "description": "页码。分页查询时使用。"
    },
    "pageSize": {
      "type": ["integer", "null"],
      "description": "每页条数。分页查询时使用。"
    },
    "clientSource": {
      "type": ["string", "null"],
      "description": "客户端标识，可选。"
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
  "required": ["dimensions", "flag", "stime", "etime"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "订单业务类型 / 订单渠道统计列表返回结果。该接口直接返回 HeaderReportVo<OrderDimensionStatsVo>，本身包含 success/code/message 等基础状态字段。",
  "$defs": {
    "head": {
      "type": "object",
      "description": "动态表头节点。既可能是普通列，也可能是分组列。",
      "properties": {
        "title": {
          "type": ["string", "null"],
          "description": "列标题。"
        },
        "key": {
          "type": ["string", "null"],
          "description": "列字段 key。动态维度列通常形如 `1_orderAmount`、`6_actualReceiptAmount`。"
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
          "description": "子列列表；存在时表示这是一个分组表头。",
          "items": {
            "$ref": "#/$defs/head"
          }
        }
      }
    },
    "orderDimensionStats": {
      "type": "object",
      "description": "单条订单业务类型 / 渠道统计记录。",
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
        "days": {
          "type": ["integer", "null"],
          "description": "营业天数。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "流水金额。"
        },
        "incUnPayOrderAmount": {
          "type": ["number", "null"],
          "description": "营业流水（含待结）。仅当 metrics 中包含该指标时返回。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实收金额。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额。"
        },
        "discountAmountRate": {
          "type": ["string", "null"],
          "description": "优惠占比。"
        },
        "saleOrderNum": {
          "type": ["integer", "null"],
          "description": "有效订单数。"
        },
        "disFrontOrderAverage": {
          "type": ["number", "null"],
          "description": "折前单均。"
        },
        "disAfterOrderAverage": {
          "type": ["number", "null"],
          "description": "折后单均。"
        },
        "customerNum": {
          "type": ["integer", "null"],
          "description": "客流量。"
        },
        "disBeforePersonAvg": {
          "type": ["number", "null"],
          "description": "折前人均。"
        },
        "disAfterPersonAvg": {
          "type": ["number", "null"],
          "description": "折后人均。"
        },
        "chainOrderAmountRate": {
          "type": ["number", "null"],
          "description": "流水金额环比。"
        },
        "chainIncUnPayOrderAmountRate": {
          "type": ["number", "null"],
          "description": "营业流水（含待结）环比。"
        },
        "chainActualReceiptAmountRate": {
          "type": ["number", "null"],
          "description": "实收金额环比。"
        },
        "chainCustomerNumRate": {
          "type": ["number", "null"],
          "description": "客流量环比。"
        },
        "chainSaleOrderNumRate": {
          "type": ["number", "null"],
          "description": "有效订单数环比。"
        },
        "map": {
          "type": ["object", "null"],
          "description": "动态维度指标集合。key 形如 `维度编码_指标编码`。当 dimensions=1 时，维度编码通常对应业务类型，如 `1-自提`、`2-外卖`、`3-堂食`、`4-外带`；当 dimensions=2 时，通常对应渠道编码，如 `1-美团`、`5-商家小程序`、`6-收银POS` 等。",
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
        "$ref": "#/$defs/orderDimensionStats"
      }
    },
    "sum": {
      "$ref": "#/$defs/orderDimensionStats"
    },
    "headList": {
      "type": ["array", "null"],
      "description": "动态表头定义。固定列和按业务类型 / 渠道展开的动态列都会出现在这里。",
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
  "dimensions": 1,
  "flag": 2,
  "stime": 20260301,
  "etime": 20260307,
  "pageNo": 1,
  "pageSize": 20,
  "metrics": [
    "orderAmount",
    "actualReceiptAmount",
    "discountAmount",
    "saleOrderNum"
  ]
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/getOrderDimensionStatsList' '{"groupKey":1,"dimensions":1,"flag":2,"stime":20260301,"etime":20260307,"pageNo":1,"pageSize":20,"metrics":["orderAmount","actualReceiptAmount","discountAmount","saleOrderNum"]}'
```
