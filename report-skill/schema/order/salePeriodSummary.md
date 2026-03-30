# 查询销售时段 / 餐段统计表

## 接口基本信息

- 原始路径 (path): `/report/salePeriodSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内按时段或餐段汇总的销售统计数据，返回分页列表、合计行和动态表头。结果可按门店、城市、省份等维度展示流水金额、实收金额、订单数、客流和人均/单均指标。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  `viewType = 1` 时必须传 `orgId`，且服务端会忽略 `statisticsDimension`；`viewType = 2` 时会按集团视角统计，可选 `statisticsDimension = 1-门店 / 2-城市 / 3-省份`。
  `dateType = 2` 且时间只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  `periodMethod` 为空时，服务端默认按 `1-时段` 处理；当 `periodMethod = 1` 时，`periodType` 必填。
  `columns` 为空时，服务端默认返回完整指标列：流水金额、流水金额占比、实收金额、实收金额占比、有效订单数、有效订单数占比、折前 / 折后单均、客流量、折前 / 折后人均。
  当 `businessTypes` 为空且集团开启会员权益卡销售参数时，服务端会默认补充业务类型 `1,2,3,4,8`。
  返回体是 `HeaderReportVo<SalePeriodSummaryVo>`，其中 `headList` 会随着 `periodMethod`、`viewType`、`statisticsDimension`、`timeMethod` 和列配置动态变化。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 哪些时段或餐段贡献了最高的流水金额、实收金额和订单量，是否存在明显高峰。
2. 不同时段 / 餐段的客流、人均和单均差异是否显著，是否呈现不同经营结构。
3. 集团视角下，不同门店 / 城市 / 省份在相同时段的表现是否分化明显。
4. 某些时段订单量高但实收偏低，或客流高但人均偏低时，应提醒用户关注优惠或低客单问题。
5. 如果尾部时段贡献极低但仍占用营业资源，可提示用户进一步评估营业安排。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询销售时段 / 餐段统计表请求参数。原始路径: /report/salePeriodSummary",
  "properties": {
    "viewType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "orgId": {
      "type": ["integer", "null"],
      "description": "门店 ID。viewType=1 时必填。"
    },
    "orgIds": {
      "type": ["array", "null"],
      "description": "门店 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "dateType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "日期类型。1-营业日期，2-销售日期。"
    },
    "startDate": {
      "type": ["integer", "string"],
      "description": "开始时间。通常传 8 位日期 yyyyMMdd；当 dateType=2 时服务端会自动补齐时分秒。"
    },
    "endDate": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd；当 dateType=2 时服务端会自动补齐时分秒。"
    },
    "periodMethod": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "统计方式。1-时段，2-餐段。为空时默认 1。"
    },
    "periodType": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "统计间隔。1-15分钟，2-半小时，3-小时。periodMethod=1 时必填。"
    },
    "statisticsDimension": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "集团视角下的统计维度。1-门店，2-城市，3-省份。viewType=1 时会被忽略。"
    },
    "columns": {
      "type": ["array", "null"],
      "description": "需要返回的指标列 key 列表。不传时返回默认完整列。",
      "items": {
        "type": "string",
        "enum": [
          "orderAmount",
          "orderAmountRate",
          "actualReceiptAmount",
          "actualReceiptAmountRate",
          "saleOrderNum",
          "saleOrderNumRate",
          "disFrontOrderAverage",
          "disAfterOrderAverage",
          "customerNum",
          "disBeforePersonAvg",
          "disAfterPersonAvg"
        ]
      }
    },
    "businessTypes": {
      "type": ["array", "null"],
      "description": "业务类型列表。为空时服务端可能按集团参数补默认值。",
      "items": {
        "type": "integer"
      }
    },
    "platformTypeList": {
      "type": ["array", "null"],
      "description": "订单渠道列表。",
      "items": {
        "type": "integer"
      }
    },
    "timeMethod": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "汇总方式。0-日期汇总（默认），1-单日明细。"
    },
    "zcMealTimeType": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "餐段时间口径。0-按开单时间，1-按结账时间，默认 1。"
    },
    "categoryIds": {
      "type": ["array", "null"],
      "description": "B 端分类 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "offlineCategoryIds": {
      "type": ["array", "null"],
      "description": "POS 分类 ID 列表。",
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
      "description": "是否交班。代码注释标明该字段在此接口中不使用。"
    },
    "isTest": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否查询测试单。代码注释标明该字段在此接口中不使用。"
    },
    "trainingMode": {
      "type": ["integer", "null"],
      "description": "练习标识。0-正常，1-测试。"
    },
    "pageNo": {
      "type": ["integer", "null"],
      "description": "页码。"
    },
    "pageSize": {
      "type": ["integer", "null"],
      "description": "每页条数。"
    }
  },
  "required": ["viewType", "dateType", "startDate", "endDate"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "销售时段 / 餐段统计表返回结果。该接口直接返回 HeaderReportVo<SalePeriodSummaryVo>，本身包含 success/code/message 等基础状态字段。",
  "$defs": {
    "head": {
      "type": "object",
      "description": "动态表头定义。",
      "properties": {
        "title": {
          "type": ["string", "null"],
          "description": "列标题。"
        },
        "key": {
          "type": ["string", "null"],
          "description": "列字段 key。"
        },
        "type": {
          "type": ["string", "null"],
          "description": "列类型，例如文本、数值、比例等。"
        },
        "precision": {
          "type": ["integer", "null"],
          "description": "数值精度。"
        },
        "width": {
          "type": ["integer", "null"],
          "description": "列宽。"
        }
      }
    },
    "salePeriodSummary": {
      "type": "object",
      "description": "单条销售时段 / 餐段统计记录。",
      "properties": {
        "orgCode": {
          "type": ["string", "null"],
          "description": "门店编码。集团视角 + 门店维度时返回。"
        },
        "shopName": {
          "type": ["string", "null"],
          "description": "门店名称。集团视角 + 门店维度时返回。"
        },
        "cityName": {
          "type": ["string", "null"],
          "description": "城市名称。集团视角 + 城市维度时返回。"
        },
        "provinceName": {
          "type": ["string", "null"],
          "description": "省份名称。集团视角 + 省份维度时返回。"
        },
        "period": {
          "type": ["string", "null"],
          "description": "时段展示文本。periodMethod=1 时返回，例如 `09:00-09:15`。"
        },
        "timeName": {
          "type": ["string", "null"],
          "description": "餐段名称。periodMethod=2 时返回。"
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
        "saleOrderNum": {
          "type": ["integer", "null"],
          "description": "有效订单数。"
        },
        "saleOrderNumRate": {
          "type": ["string", "null"],
          "description": "有效订单数占比。"
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
        "workDate": {
          "type": ["integer", "null"],
          "description": "营业日期。仅在 timeMethod=1 时通常返回。"
        },
        "periodStart": {
          "type": ["string", "null"],
          "description": "时段开始时间原始值，用于服务端组装 period。"
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
        "$ref": "#/$defs/salePeriodSummary"
      }
    },
    "sum": {
      "$ref": "#/$defs/salePeriodSummary"
    },
    "headList": {
      "type": ["array", "null"],
      "description": "动态表头定义，会根据 periodMethod、viewType、statisticsDimension、timeMethod 和 columns 动态变化。",
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
  "viewType": 1,
  "orgId": 20001,
  "dateType": 1,
  "startDate": 20260301,
  "endDate": 20260307,
  "periodMethod": 1,
  "periodType": 3,
  "columns": [
    "orderAmount",
    "orderAmountRate",
    "actualReceiptAmount",
    "saleOrderNum",
    "customerNum"
  ],
  "pageNo": 1,
  "pageSize": 20
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/salePeriodSummary' '{"viewType":1,"orgId":20001,"dateType":1,"startDate":20260301,"endDate":20260307,"periodMethod":1,"periodType":3,"columns":["orderAmount","orderAmountRate","actualReceiptAmount","saleOrderNum","customerNum"],"pageNo":1,"pageSize":20}'
```
