# 查询商品综合统计

## 接口基本信息

- 原始路径 (path): `/report/overviewGoodsSummary`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的商品综合统计，返回销售数量、退货数量、赠送数量、销售实收、退货金额，以及商品销售排行、分类销售排行、退货商品排行、退货原因排行和赠送原因排行。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  当 `period` 为空时，服务端会默认按 `3-自定义` 处理。
  调用入口会先执行 `dealQueryParams(dto)`，因此组织范围与业务权限会按平台标准逻辑补齐。
  `pickupSumMedhod` 和 `takeoutSumMedhod` 会影响 `businessType` 的归并口径，例如自提并入外卖、自提并入堂食或外带并入堂食。
  销售类汇总字段按“销售 - 退货”口径计算，退货字段单独统计，赠送字段按赠品订单正负向冲减计算。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 销售数量、退货数量、赠送数量的整体结构，判断商品经营是否存在明显退货或赠送压力。
2. 商品销售排行和分类销售排行是否高度集中，判断核心爆款或核心品类依赖度。
3. 哪些商品退货较多、哪些退货原因靠前，识别商品质量、制作、履约或操作问题。
4. 赠送原因排行是否异常集中，判断是否存在赠送过多、补偿过多或运营策略波动。
5. 如果销售数量与销售实收、退货数量与退货金额之间明显不协调，应提醒用户关注商品口径、价格带或异常数据。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询商品综合统计请求参数。原始路径: /report/overviewGoodsSummary",
  "properties": {
    "orgId": {
      "type": ["integer", "null"],
      "description": "门店 ID。与 orgIdList 二选一或同时传递。"
    },
    "orgIdList": {
      "type": ["array", "null"],
      "description": "门店 ID 列表。",
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
      "description": "开始时间。通常传 8 位日期 yyyyMMdd。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd。"
    },
    "period": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "统计周期。为空时默认 3-自定义。"
    },
    "viewType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "businessType": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, null],
      "description": "业务类型。1-自提，2-外卖，3-堂食，4-外带。"
    },
    "goodsFlag": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, 4, 5, null],
      "description": "商品统计口径。1-单品，2-套餐，3-套餐明细，4-单品+套餐明细，5-单品+套餐。"
    },
    "goodsTypeList": {
      "type": ["array", "null"],
      "description": "商品类型列表。",
      "items": {
        "type": "integer"
      }
    },
    "pickupSumMedhod": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "自提统计方式。1-自提单独统计，2-自提归入外卖，3-自提归入堂食。默认 1。"
    },
    "takeoutSumMedhod": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "外带统计方式。1-外带单独统计，2-外带归入堂食。默认 1。"
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
  "required": ["flag", "stime", "etime"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "商品综合统计返回结果。该接口直接返回 OverviewGoodsSummaryVo，本身包含 success/code/message 等基础状态字段，不再额外包一层 data。",
  "$defs": {
    "salesRanking": {
      "type": "object",
      "description": "商品销售排行或分类销售排行。",
      "properties": {
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。分类排行中通常为空。"
        },
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。分类排行中通常为空。"
        },
        "goodsCode": {
          "type": ["string", "null"],
          "description": "商品编码。"
        },
        "categoryId": {
          "type": ["integer", "null"],
          "description": "分类 ID。"
        },
        "categoryName": {
          "type": ["string", "null"],
          "description": "分类名称。"
        },
        "orderNum": {
          "type": ["integer", "null"],
          "description": "订单数量。"
        },
        "goodsNum": {
          "type": ["number", "null"],
          "description": "销售数量。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "销售金额。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实收金额。"
        }
      }
    },
    "refundRanking": {
      "type": "object",
      "description": "退货商品排行或退货原因排行。",
      "properties": {
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。退货原因排行中通常为空。"
        },
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。"
        },
        "refundReason": {
          "type": ["string", "null"],
          "description": "退货原因。"
        },
        "refundNum": {
          "type": ["integer", "null"],
          "description": "退单数量。"
        },
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "点单数量。"
        },
        "refundGoodsNum": {
          "type": ["number", "null"],
          "description": "退货数量。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实际退货金额。"
        },
        "refundAmount": {
          "type": ["number", "null"],
          "description": "退货金额。"
        }
      }
    },
    "giftRanking": {
      "type": "object",
      "description": "赠送原因排行。",
      "properties": {
        "giveGoodsReson": {
          "type": ["string", "null"],
          "description": "赠菜原因。"
        },
        "giftNum": {
          "type": ["number", "null"],
          "description": "赠送数量。"
        },
        "giftAmount": {
          "type": ["number", "null"],
          "description": "赠送金额。"
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
      "description": "销售商品数量，按 销售 - 退货 口径计算。"
    },
    "refundGoodsNum": {
      "type": ["number", "null"],
      "description": "退货商品数量。"
    },
    "giveGoodsNum": {
      "type": ["number", "null"],
      "description": "赠送商品数量，按正负向冲减后统计。"
    },
    "saleActualReceiptAmount": {
      "type": ["number", "null"],
      "description": "销售实收金额，按 销售 - 退货 口径计算。"
    },
    "refundActualReceiptAmount": {
      "type": ["number", "null"],
      "description": "退货实收金额。"
    },
    "refundAmount": {
      "type": ["number", "null"],
      "description": "退货流水金额。"
    },
    "giveGoodsAmount": {
      "type": ["number", "null"],
      "description": "赠送流水金额，按正负向冲减后统计。"
    },
    "chainSaleGoodsRate": {
      "type": ["number", "null"],
      "description": "销售数量环比。"
    },
    "chainRefundGoodsRate": {
      "type": ["number", "null"],
      "description": "退货数量环比。"
    },
    "chainRefundActualReceiptAmountRate": {
      "type": ["number", "null"],
      "description": "实际退货金额环比。"
    },
    "chainRefundAmountRate": {
      "type": ["number", "null"],
      "description": "退货流水金额环比。"
    },
    "chainGiveGoodsNumRate": {
      "type": ["number", "null"],
      "description": "赠送数量环比。"
    },
    "chainGiveGoodsAmountRate": {
      "type": ["number", "null"],
      "description": "赠送金额环比。"
    },
    "sameSaleGoodsRate": {
      "type": ["number", "null"],
      "description": "销售数量同比。"
    },
    "sameRefundGoodsRate": {
      "type": ["number", "null"],
      "description": "退货数量同比。"
    },
    "sameRefundActualReceiptAmountRate": {
      "type": ["number", "null"],
      "description": "实际退货金额同比。"
    },
    "sameRefundAmountRate": {
      "type": ["number", "null"],
      "description": "退货流水金额同比。"
    },
    "sameGiveGoodsNumRate": {
      "type": ["number", "null"],
      "description": "赠送数量同比。"
    },
    "sameGiveGoodsAmountRate": {
      "type": ["number", "null"],
      "description": "赠送金额同比。"
    },
    "goodsRankingList": {
      "type": ["array", "null"],
      "description": "商品销售排行列表。",
      "items": {
        "$ref": "#/$defs/salesRanking"
      }
    },
    "categoryRankingList": {
      "type": ["array", "null"],
      "description": "分类销售排行列表。",
      "items": {
        "$ref": "#/$defs/salesRanking"
      }
    },
    "goodsRefundRankingList": {
      "type": ["array", "null"],
      "description": "退货商品排行列表。",
      "items": {
        "$ref": "#/$defs/refundRanking"
      }
    },
    "refundReasonRankingList": {
      "type": ["array", "null"],
      "description": "退货原因排行列表。",
      "items": {
        "$ref": "#/$defs/refundRanking"
      }
    },
    "giftReasonRankingList": {
      "type": ["array", "null"],
      "description": "赠送原因排行列表。",
      "items": {
        "$ref": "#/$defs/giftRanking"
      }
    },
    "updateTime": {
      "type": ["string", "null"],
      "description": "数据更新时间，格式通常为 yyyy-MM-dd HH:mm:ss。"
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
  "businessType": 2,
  "goodsFlag": 4,
  "pickupSumMedhod": 1,
  "takeoutSumMedhod": 1
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/overviewGoodsSummary' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"period":3,"businessType":2,"goodsFlag":4,"pickupSumMedhod":1,"takeoutSumMedhod":1}'
```
