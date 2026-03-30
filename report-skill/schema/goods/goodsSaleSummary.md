# 查询商品销售统计表

## 接口基本信息

- 原始路径 (path): `/report/goodsSaleSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的商品销售统计数据，返回分页列表、合计行和动态表头。可按 B 端分类、商品、商品规格、POS 分类等方式统计，并支持门店 / 城市 / 省份视角下的销售数量、销售额、商品收入、优惠金额、商品销售千次、商品点击率和顾客点击率等指标。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  `statisticsType` 或 `statisticsTypes` 至少要传一个；这是本接口的核心分组方式。
  `viewType = 1` 时必须传 `orgId`，且服务端会忽略 `statisticsDimension`；`viewType = 2` 时可选 `statisticsDimension = 1-门店 / 2-城市 / 3-省份`。
  `goodsFlag` 为空时服务端默认按 `4-单品+套餐明细` 处理，并据此自动换算 `goodsTypeList`。
  普通 `/report/goodsSaleSummary` 接口默认排序方向是 `sortType = 1`，若未显式传排序字段，服务端会按统计维度、分类、商品编码、规格等组合字段自动拼接默认排序。
  `businessTypes` 为空时，若集团开启会员权益卡销售参数，服务端会默认补 `1,2,3,4,8`。
  当 `saleRateType = 1` 时，占比指标按本次查询的总合计计算；当 `saleRateType = 2` 且 `statisticsDimension = 1` 时，占比会按各门店自己的合计重新计算。
  返回体是 `HeaderReportVo<GoodsSaleSummaryVo>`，`headList` 会随 `statisticsTypes`、`viewType`、`statisticsDimension` 动态变化。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 哪些分类、商品或规格贡献了最高的销售数量、销售额和商品收入。
2. 哪些商品销售额高但商品收入偏低，可能存在较高优惠或折扣压力。
3. 商品销售千次、商品点击率、顾客点击率能否反映出明显的头部商品和长尾商品差异。
4. 在集团视角下，不同门店 / 城市 / 省份的商品结构是否显著不同。
5. 如果某些商品销量高但订单渗透率低，或顾客点击率异常低，应提示用户进一步核对商品组合或展示策略。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询商品销售统计表请求参数。原始路径: /report/goodsSaleSummary",
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
      "description": "开始时间。通常传 8 位日期 yyyyMMdd；dateType=2 时服务端常按销售时间口径处理。"
    },
    "endDate": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd。"
    },
    "statisticsType": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, 5, null],
      "description": "统计方式（单选）。1-B端分类，2-商品，3-商品+规格，4-POS分类，5-商品+规格+销售分类。"
    },
    "statisticsTypes": {
      "type": ["array", "null"],
      "description": "统计方式（多选）。1-B端分类，2-商品，3-商品+规格。传单选 statisticsType 时服务端会自动转成该列表。",
      "items": {
        "type": "integer",
        "enum": [1, 2, 3, 4, 5]
      }
    },
    "statisticsDimension": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "集团视角下的统计维度。1-门店，2-城市，3-省份。viewType=1 时会被忽略。"
    },
    "businessTypes": {
      "type": ["array", "null"],
      "description": "业务类型列表。",
      "items": {
        "type": "integer"
      }
    },
    "platformTypes": {
      "type": ["array", "null"],
      "description": "订单渠道列表。",
      "items": {
        "type": "integer"
      }
    },
    "groupMethods": {
      "type": ["array", "null"],
      "description": "分组方式。1-业务类型，2-渠道。",
      "items": {
        "type": "integer",
        "enum": [1, 2]
      }
    },
    "goodsFlag": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, 5, null],
      "description": "商品类型组合。1-单品，2-套餐，3-套餐明细，4-单品+套餐明细（默认），5-单品+套餐。"
    },
    "goodsTypeList": {
      "type": ["array", "null"],
      "description": "商品类型列表。通常由服务端根据 goodsFlag 自动生成。",
      "items": {
        "type": "integer"
      }
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
    "goodsIds": {
      "type": ["array", "null"],
      "description": "SKU ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "goodsIdList": {
      "type": ["array", "null"],
      "description": "商品 goodsId 列表。",
      "items": {
        "type": "integer"
      }
    },
    "incomeSubjectIds": {
      "type": ["array", "null"],
      "description": "收入科目 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "cashierIdList": {
      "type": ["array", "null"],
      "description": "收银员 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "goodsNameList": {
      "type": ["array", "null"],
      "description": "商品名称列表。",
      "items": {
        "type": "string"
      }
    },
    "timeIdList": {
      "type": ["array", "null"],
      "description": "餐段 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "classesList": {
      "type": ["array", "null"],
      "description": "班次列表。",
      "items": {
        "type": "string"
      }
    },
    "saleRateType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "销售占比口径。1-所有门店总合计，2-单个门店各自合计。默认 1。"
    },
    "periodType": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "统计间隔。1-15分钟，2-半小时，3-小时，4-餐段。默认 1。"
    },
    "zcMealTimeType": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "餐段时间口径。0-按开单时间，1-按结账时间。默认 1。"
    },
    "sortField": {
      "type": ["string", "null"],
      "description": "排序字段。为空时服务端会自动生成默认排序。"
    },
    "sortType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "排序方式。1-升序，2-降序。为空时默认 1。"
    },
    "clientSource": {
      "type": ["string", "null"],
      "description": "客户端标识。"
    },
    "shiftStatus": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否交班。代码注释标明该字段在商品类接口中通常不使用。"
    },
    "isTest": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否查询测试单。代码注释标明该字段在商品类接口中通常不使用。"
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
  "description": "商品销售统计表返回结果。该接口直接返回 HeaderReportVo<GoodsSaleSummaryVo>，本身包含 success/code/message 等基础状态字段。",
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
    "goodsSaleSummary": {
      "type": "object",
      "description": "单条商品销售统计记录。",
      "properties": {
        "orgCode": {
          "type": ["string", "null"],
          "description": "门店编码。集团视角 + 门店维度时返回。"
        },
        "shopName": {
          "type": ["string", "null"],
          "description": "门店名称。集团视角 + 门店维度时返回。"
        },
        "orgId": {
          "type": ["integer", "null"],
          "description": "门店 ID。"
        },
        "cityName": {
          "type": ["string", "null"],
          "description": "城市名称。集团视角 + 城市维度时返回。"
        },
        "provinceName": {
          "type": ["string", "null"],
          "description": "省份名称。集团视角 + 省份维度时返回。"
        },
        "categoryName": {
          "type": ["string", "null"],
          "description": "B 端分类名称。"
        },
        "offlineCategoryName": {
          "type": ["string", "null"],
          "description": "POS 分类名称。"
        },
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。"
        },
        "goodsCode": {
          "type": ["string", "null"],
          "description": "商品编码。"
        },
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。"
        },
        "skuId": {
          "type": ["integer", "null"],
          "description": "SKU ID。"
        },
        "specs": {
          "type": ["string", "null"],
          "description": "规格。"
        },
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "销售数量。"
        },
        "saleGoodsNumRate": {
          "type": ["string", "null"],
          "description": "销售数量占比。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "销售额 / 流水金额。"
        },
        "orderAmountRate": {
          "type": ["string", "null"],
          "description": "销售额占比。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入。"
        },
        "actualReceiptAmountRate": {
          "type": ["string", "null"],
          "description": "商品收入占比。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额。"
        },
        "discountAmountRate": {
          "type": ["string", "null"],
          "description": "优惠金额占比。"
        },
        "saleOrderNum": {
          "type": ["integer", "null"],
          "description": "有效订单数。普通返回中有时会被整体总单量覆盖。"
        },
        "goodsSaleOrderNum": {
          "type": ["integer", "null"],
          "description": "商品销售有效订单数。"
        },
        "goodsSaleThousand": {
          "type": ["number", "null"],
          "description": "商品销售千次。"
        },
        "goodsClickPercent": {
          "type": ["string", "null"],
          "description": "商品点击率。"
        },
        "customerClickPercent": {
          "type": ["string", "null"],
          "description": "顾客点击率。"
        },
        "customerNum": {
          "type": ["integer", "null"],
          "description": "总顾客数量。普通返回中有时会被整体总客流覆盖。"
        },
        "businessType": {
          "type": ["integer", "null"],
          "description": "业务类型编码。"
        },
        "businessTypeName": {
          "type": ["string", "null"],
          "description": "业务类型名称。"
        },
        "platformType": {
          "type": ["integer", "null"],
          "description": "渠道类型编码。"
        },
        "platformTypeName": {
          "type": ["string", "null"],
          "description": "渠道类型名称。"
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
        "$ref": "#/$defs/goodsSaleSummary"
      }
    },
    "sum": {
      "$ref": "#/$defs/goodsSaleSummary"
    },
    "headList": {
      "type": ["array", "null"],
      "description": "动态表头定义，会根据统计方式和视角维度动态变化。",
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
  "statisticsType": 3,
  "goodsFlag": 4,
  "saleRateType": 1,
  "pageNo": 1,
  "pageSize": 20
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/goodsSaleSummary' '{"viewType":1,"orgId":20001,"dateType":1,"startDate":20260301,"endDate":20260307,"statisticsType":3,"goodsFlag":4,"saleRateType":1,"pageNo":1,"pageSize":20}'
```
