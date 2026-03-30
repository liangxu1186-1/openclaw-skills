# 查询销售日报表统计

## 接口基本信息

- 原始路径 (path): `/report/orderBusinessDaily`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的销售日报表统计，返回商品汇总、实收和优惠明细、业务类型分布、商品销售排行、商品分类排行，以及部分 POS 专属的餐段、挂账、敏感操作和储值业务明细。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  当 `businessTypeList` 为空时，服务端默认按普通订单业务类型 `1,2,3,4` 查询。
  当 `flag = 1` 且 `stime` / `etime` 只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  `dailyCateVo`、`businessTimeList`、`companyTransDetailList`、`sensitiveOperList` 以及各类储值/权益卡拆分明细，只会在 POS 来源请求下稳定返回；非 POS 来源可能为空。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询销售日报表统计请求参数。原始路径: /report/orderBusinessDaily",
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
      "description": "日期标识。1-销售日，2-营业日，3-开台日。该接口服务内主要按 1 和 2 处理。"
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
      "description": "统计周期。该接口主流程对该字段依赖较弱，可选。"
    },
    "viewType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "businessTypeList": {
      "type": ["array", "null"],
      "description": "业务类型过滤条件。不传时默认查询 1、2、3、4。",
      "items": {
        "type": "integer"
      }
    },
    "platformTypeList": {
      "type": ["array", "null"],
      "description": "订单渠道过滤条件。",
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
    "operationTypeList": {
      "type": ["array", "null"],
      "description": "敏感操作类型列表。1-单品优惠，2-整单优惠，3-改价，4-赠送，5-重结，6-退货，7-退款，8-反结账。",
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
  "required": ["flag", "stime", "etime"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "销售日报表统计返回结果。该接口直接返回 OrderBusinessDailyVo，本身包含 success/code/message 等基础状态字段，不再额外包一层 data。",
  "$defs": {
    "paySubjectSummary": {
      "type": "object",
      "description": "支付科目或优惠科目汇总。",
      "properties": {
        "businessType": {
          "type": ["integer", "null"],
          "description": "业务类型编码。"
        },
        "paySubjectName": {
          "type": ["string", "null"],
          "description": "支付科目名称。"
        },
        "actualReceiptAmount": {
          "type": ["string", "null"],
          "description": "实收金额或储值金额。"
        },
        "disCountAmount": {
          "type": ["string", "null"],
          "description": "优惠金额。"
        },
        "useNum": {
          "type": ["integer", "null"],
          "description": "执行次数或交易笔数。"
        }
      }
    },
    "promotionDetailInfo": {
      "type": "object",
      "description": "平台券或优惠券明细。",
      "properties": {
        "promotionName": {
          "type": ["string", "null"],
          "description": "券名称。"
        },
        "count": {
          "type": ["integer", "null"],
          "description": "券张数。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实收金额。"
        }
      }
    },
    "promotionDetail": {
      "type": "object",
      "description": "按支付科目分组的平台券核销明细。",
      "properties": {
        "paySubjectCode": {
          "type": ["string", "null"],
          "description": "支付科目编码。"
        },
        "paySubjectName": {
          "type": ["string", "null"],
          "description": "支付科目名称。"
        },
        "promotionDetailInfos": {
          "type": ["array", "null"],
          "description": "该支付科目下的优惠券明细。",
          "items": {
            "$ref": "#/$defs/promotionDetailInfo"
          }
        }
      }
    },
    "businessTypeSummary": {
      "type": "object",
      "description": "业务类型汇总。",
      "properties": {
        "businessTypeName": {
          "type": ["string", "null"],
          "description": "业务类型名称。"
        },
        "businessType": {
          "type": ["integer", "null"],
          "description": "业务类型编码。"
        },
        "orderNum": {
          "type": ["integer", "null"],
          "description": "交易笔数。"
        },
        "actualReceiptAmount": {
          "type": ["string", "null"],
          "description": "实收金额。"
        },
        "orderAverage": {
          "type": ["string", "null"],
          "description": "客单价。"
        },
        "businessTypeRate": {
          "type": ["string", "null"],
          "description": "实收占比。"
        }
      }
    },
    "dailyGoodsSummary": {
      "type": "object",
      "description": "商品销售排行明细。",
      "properties": {
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。"
        },
        "skuId": {
          "type": ["integer", "null"],
          "description": "SKU ID。"
        },
        "isWeigh": {
          "type": ["integer", "null"],
          "description": "是否称重商品。1-是，0-否。"
        },
        "goodsType": {
          "type": ["integer", "null"],
          "description": "商品类型。"
        },
        "saleUnit": {
          "type": ["string", "null"],
          "description": "售卖单位。"
        },
        "goodsName": {
          "type": ["string", "null"],
          "description": "商品名称。"
        },
        "orderAmount": {
          "type": ["string", "null"],
          "description": "流水金额。"
        },
        "goodsPayAmount": {
          "type": ["string", "null"],
          "description": "产品成交金额。"
        },
        "actualReceiptAmount": {
          "type": ["string", "null"],
          "description": "实收金额。"
        },
        "saleGoodsNum": {
          "type": ["string", "null"],
          "description": "销售数量。"
        }
      }
    },
    "dailyGoodsStats": {
      "type": "object",
      "description": "单点、套餐或合计销售排行汇总。",
      "properties": {
        "orderAmount": {
          "type": ["string", "null"],
          "description": "流水金额。"
        },
        "goodsPayAmount": {
          "type": ["string", "null"],
          "description": "产品成交金额。"
        },
        "actualReceiptAmount": {
          "type": ["string", "null"],
          "description": "实收金额。"
        },
        "saleGoodsNum": {
          "type": ["string", "null"],
          "description": "销售数量。"
        },
        "goodsSummaryList": {
          "type": ["array", "null"],
          "description": "商品排行明细列表。",
          "items": {
            "$ref": "#/$defs/dailyGoodsSummary"
          }
        }
      }
    },
    "categorySummary": {
      "type": "object",
      "description": "商品分类排行明细。",
      "properties": {
        "offlineCategoryName": {
          "type": ["string", "null"],
          "description": "POS 分类名称。"
        },
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "销售数量。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "销售额。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入。"
        },
        "goodsPosCateSaleSummaryVos": {
          "type": ["array", "null"],
          "description": "分类下的商品明细排行。",
          "items": {
            "type": "object",
            "properties": {
              "goodsName": {
                "type": ["string", "null"],
                "description": "商品名称。"
              },
              "specs": {
                "type": ["string", "null"],
                "description": "商品规格。"
              },
              "saleGoodsNum": {
                "type": ["number", "null"],
                "description": "销售数量。"
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
          }
        }
      }
    },
    "dailyCate": {
      "type": "object",
      "description": "商品分类排行汇总。",
      "properties": {
        "saleGoodsNum": {
          "type": ["number", "null"],
          "description": "销售数量合计。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "销售额合计。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入合计。"
        },
        "goodsPosCateSaleSummaryVos": {
          "type": ["array", "null"],
          "description": "分类排行列表。",
          "items": {
            "$ref": "#/$defs/categorySummary"
          }
        }
      }
    },
    "businessTimeSummary": {
      "type": "object",
      "description": "营业餐段统计。",
      "properties": {
        "timeName": {
          "type": ["string", "null"],
          "description": "餐段名称。"
        },
        "timeId": {
          "type": ["integer", "null"],
          "description": "餐段 ID。"
        },
        "customerNum": {
          "type": ["number", "null"],
          "description": "客流量。"
        },
        "saleOrderNum": {
          "type": ["number", "null"],
          "description": "销售单数。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入。"
        }
      }
    },
    "companyTransDetail": {
      "type": "object",
      "description": "客户挂账明细。",
      "properties": {
        "companyId": {
          "type": ["integer", "null"],
          "description": "公司 ID。"
        },
        "companyName": {
          "type": ["string", "null"],
          "description": "公司名称。"
        },
        "saleOrderNum": {
          "type": ["number", "null"],
          "description": "销售单数。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "商品收入。"
        }
      }
    },
    "sensitiveOperSummary": {
      "type": "object",
      "description": "敏感操作统计。",
      "properties": {
        "operationName": {
          "type": ["string", "null"],
          "description": "敏感操作名称。"
        },
        "operationNum": {
          "type": ["number", "null"],
          "description": "次数。"
        },
        "operationAmount": {
          "type": ["number", "null"],
          "description": "金额。"
        }
      }
    },
    "storedSummary": {
      "type": "object",
      "description": "储值或会员卡相关业务汇总。",
      "properties": {
        "businessType": {
          "type": ["integer", "null"],
          "description": "业务类型编码。"
        },
        "orderNum": {
          "type": ["integer", "null"],
          "description": "交易笔数。"
        },
        "orderTotalAmount": {
          "type": ["string", "null"],
          "description": "正向售卖金额。"
        },
        "refundTotalAmount": {
          "type": ["string", "null"],
          "description": "逆向退款金额。"
        },
        "vipRefundTotalAmount": {
          "type": ["string", "null"],
          "description": "会员退款金额。"
        },
        "storedTotalAmount": {
          "type": ["string", "null"],
          "description": "净储值金额。"
        }
      }
    },
    "dailyBusinessSummary": {
      "type": "object",
      "description": "特定业务类型的汇总数据。",
      "properties": {
        "orderNum": {
          "type": ["integer", "null"],
          "description": "交易笔数。"
        },
        "orderTotalAmount": {
          "type": ["string", "null"],
          "description": "售卖金额。"
        },
        "refundTotalAmount": {
          "type": ["string", "null"],
          "description": "退款金额。"
        },
        "receiptTotalAmount": {
          "type": ["string", "null"],
          "description": "收款总额。"
        }
      }
    },
    "dailyBusinessDetail": {
      "type": "object",
      "description": "特定业务类型的支付与退款明细。",
      "properties": {
        "payList": {
          "type": ["array", "null"],
          "description": "收款支付明细。",
          "items": {
            "$ref": "#/$defs/paySubjectSummary"
          }
        },
        "refundList": {
          "type": ["array", "null"],
          "description": "退款支付明细。",
          "items": {
            "$ref": "#/$defs/paySubjectSummary"
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
    "goodsSaleDailySummaryVo": {
      "type": ["object", "null"],
      "description": "商品汇总。",
      "properties": {
        "orderNum": {
          "type": ["integer", "null"],
          "description": "交易笔数。"
        },
        "refundOrderNum": {
          "type": ["integer", "null"],
          "description": "退货笔数。"
        },
        "orderTotalAmount": {
          "type": ["string", "null"],
          "description": "营业流水。"
        },
        "refundTotalAmount": {
          "type": ["string", "null"],
          "description": "退货金额。"
        },
        "orderDisCountAmount": {
          "type": ["string", "null"],
          "description": "优惠金额。"
        },
        "actualReceiptAmount": {
          "type": ["string", "null"],
          "description": "实收金额。"
        },
        "orderAverage": {
          "type": ["string", "null"],
          "description": "客单价。"
        }
      }
    },
    "actualReceiptList": {
      "type": ["array", "null"],
      "description": "实收明细。",
      "items": {
        "$ref": "#/$defs/paySubjectSummary"
      }
    },
    "disCountList": {
      "type": ["array", "null"],
      "description": "优惠明细。",
      "items": {
        "$ref": "#/$defs/paySubjectSummary"
      }
    },
    "businessTypeSummaryVoList": {
      "type": ["array", "null"],
      "description": "业务类型汇总列表。",
      "items": {
        "$ref": "#/$defs/businessTypeSummary"
      }
    },
    "goodsSaleStats": {
      "$ref": "#/$defs/dailyGoodsStats"
    },
    "setMealSaleStats": {
      "$ref": "#/$defs/dailyGoodsStats"
    },
    "goodsSaleSum": {
      "$ref": "#/$defs/dailyGoodsStats"
    },
    "promotionDetailList": {
      "type": ["array", "null"],
      "description": "平台券核销明细。",
      "items": {
        "$ref": "#/$defs/promotionDetail"
      }
    },
    "dailyCateVo": {
      "$ref": "#/$defs/dailyCate"
    },
    "businessTimeList": {
      "type": ["array", "null"],
      "description": "营业餐段统计列表。",
      "items": {
        "$ref": "#/$defs/businessTimeSummary"
      }
    },
    "companyTransDetailList": {
      "type": ["array", "null"],
      "description": "客户挂账明细列表。",
      "items": {
        "$ref": "#/$defs/companyTransDetail"
      }
    },
    "storedPayList": {
      "type": ["array", "null"],
      "description": "储值支付明细。",
      "items": {
        "$ref": "#/$defs/paySubjectSummary"
      }
    },
    "storedSummaryVo": {
      "$ref": "#/$defs/storedSummary"
    },
    "memberStoredSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "memberStoredDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "memberRefundSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "memberRefundDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "cardDepositSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "cardDepositDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "openCardSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "openCardDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "cardCostSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "cardCostDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "giftCardSaleSummary": {
      "$ref": "#/$defs/dailyBusinessSummary"
    },
    "giftCardSaleDetail": {
      "$ref": "#/$defs/dailyBusinessDetail"
    },
    "sensitiveOperList": {
      "type": ["array", "null"],
      "description": "敏感操作统计列表。",
      "items": {
        "$ref": "#/$defs/sensitiveOperSummary"
      }
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
  "businessTypeList": [1, 2, 3, 4],
  "platformTypeList": [1, 2],
  "cashierIdList": [90001],
  "timeIdList": [1001, 1002],
  "classesList": ["午市", "晚市"],
  "shiftStatus": 0
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/orderBusinessDaily' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"businessTypeList":[1,2,3,4],"platformTypeList":[1,2],"cashierIdList":[90001],"timeIdList":[1001,1002],"classesList":["午市","晚市"],"shiftStatus":0}'
```
