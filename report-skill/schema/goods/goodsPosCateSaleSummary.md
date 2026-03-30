# 查询商品分类销售排行

## 接口基本信息

- 原始路径 (path): `/report/goodsPosCateSaleSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定门店和时间范围内的商品分类销售排行。返回顶部汇总数据、POS 分类排行，以及每个分类下的商品明细排行。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  当 `goodsFlag` 为空或为 `0` 时，服务端会自动按 `4-单品+套餐明细` 处理。
  当 `startDate` / `endDate` 传 6 位月份时，服务端会自动展开为该月首日和末日。
  当 `dateType = 2` 且时间只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 哪些分类贡献最高，包括销量、销售额和实收的领先项。
2. 哪些分类销量高但实收偏低，或营业额与实收差距明显，可能存在较多优惠、折扣或异常口径。
3. 若分类下包含商品明细，可结合头部商品判断该分类的主要贡献来源，但不要把推测当成事实。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询商品分类销售排行请求参数。原始路径: /report/goodsPosCateSaleSummary",
  "properties": {
    "viewType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "orgId": {
      "type": "integer",
      "description": "门店 ID。"
    },
    "dateType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "日期类型。1-营业日期，2-销售日期。"
    },
    "startDate": {
      "type": ["integer", "string"],
      "description": "开始时间。支持 yyyyMM、yyyyMMdd 或 yyyyMMddHHmmss；当 dateType=2 且传 8 位日期时，服务端会自动补齐到 000000。"
    },
    "endDate": {
      "type": ["integer", "string"],
      "description": "结束时间。支持 yyyyMM、yyyyMMdd 或 yyyyMMddHHmmss；当 dateType=2 且传 8 位日期时，服务端会自动补齐到 235959。"
    },
    "goodsFlag": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, 5, null],
      "description": "商品统计口径。1-单品，2-套餐，3-套餐明细，4-单品+套餐明细（默认），5-单品+套餐。"
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
      "description": "SKU ID 列表，按 sku_id 过滤。",
      "items": {
        "type": "integer"
      }
    },
    "goodsIdList": {
      "type": ["array", "null"],
      "description": "商品 goodsId 列表，按 goods_id 过滤。",
      "items": {
        "type": "integer"
      }
    },
    "goodsNameList": {
      "type": ["array", "null"],
      "description": "商品名称列表，按 goods_name 精确过滤。",
      "items": {
        "type": "string"
      }
    },
    "businessTypes": {
      "type": ["array", "null"],
      "description": "业务类型列表。不传时服务端默认按 1、2、3、4 处理；若集团开启会员卡销售能力，服务端还可能扩展到 8。",
      "items": {
        "type": "integer"
      }
    },
    "platformTypes": {
      "type": ["array", "null"],
      "description": "订单渠道类型列表。",
      "items": {
        "type": "integer"
      }
    },
    "timeIdList": {
      "type": ["array", "null"],
      "description": "餐段 ID 列表。",
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
    "classesList": {
      "type": ["array", "null"],
      "description": "班次列表。",
      "items": {
        "type": "string"
      }
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
    "trainingMode": {
      "type": ["integer", "null"],
      "description": "练习标识。0-正常，1-测试。"
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
  "description": "商品分类销售排行返回结果。该接口直接返回 PosCateVo，本身包含 success/code/message 等基础状态字段，不再额外包一层 data。",
  "$defs": {
    "goodsSummary": {
      "type": "object",
      "description": "分类下的商品销售明细。",
      "properties": {
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。"
        },
        "specs": {
          "type": ["string", "null"],
          "description": "商品规格或售卖单位。"
        },
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "销售数量。"
        },
        "setSaleGoodsNum": {
          "type": ["number", "null"],
          "description": "套餐销售数量。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "销售额。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入。"
        }
      }
    },
    "categorySummary": {
      "type": "object",
      "description": "POS 分类维度的销售排行。",
      "properties": {
        "offlineCategoryName": {
          "type": ["string", "null"],
          "description": "POS 分类名称。服务端会把空分类名转换成“临时品”。"
        },
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "分类销售数量。"
        },
        "setSaleGoodsNum": {
          "type": ["number", "null"],
          "description": "分类套餐销售数量。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "分类销售额。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "分类商品收入。"
        },
        "goodsPosCateSaleSummaryVos": {
          "type": ["array", "null"],
          "description": "该分类下的商品明细排行。",
          "items": {
            "$ref": "#/$defs/goodsSummary"
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
    "saleGoodsNum": {
      "type": ["number", "null"],
      "description": "顶部汇总销售数量。"
    },
    "setSaleGoodsNum": {
      "type": ["number", "null"],
      "description": "顶部汇总套餐销售数量。"
    },
    "orderAmount": {
      "type": ["number", "null"],
      "description": "顶部汇总销售额。"
    },
    "actualReceiptAmount": {
      "type": ["number", "null"],
      "description": "顶部汇总商品收入。"
    },
    "goodsPosCateSaleSummaryVos": {
      "type": ["array", "null"],
      "description": "POS 分类销售排行列表。",
      "items": {
        "$ref": "#/$defs/categorySummary"
      }
    }
  }
}
```

请求体示例:

```json
{
  "viewType": 1,
  "dateType": 1,
  "startDate": 20260301,
  "endDate": 20260307,
  "goodsFlag": 4,
  "offlineCategoryIds": [1001, 1002],
  "businessTypes": [1, 2, 3, 4],
  "platformTypes": [1, 2]
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/goodsPosCateSaleSummary' '{"viewType":1,"dateType":1,"startDate":20260301,"endDate":20260307,"goodsFlag":4,"offlineCategoryIds":[1001,1002],"businessTypes":[1,2,3,4],"platformTypes":[1,2]}'
```
