# 查询云助手营业指标

## 接口基本信息

- 原始路径 (path): `/report/getYzsBusinessMetrics`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围和组织范围内的云助手营业指标。返回营业额、营业收入、优惠金额、客流、订单数、退货金额，以及按业务类型和渠道类型拆分的统计结果。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定的集团自动补齐。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询云助手营业指标请求参数。原始路径: /report/getYzsBusinessMetrics",
  "properties": {
    "orgId": {
      "type": ["integer", "null"],
      "description": "组织 ID。与 orgIdList 二选一或同时传递。"
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
      "description": "开始时间。通常传 8 位日期 yyyyMMdd，例如 20260301。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd，例如 20260307。"
    },
    "period": {
      "type": "integer",
      "enum": [1, 2, 3, 4, 5, 6],
      "description": "统计周期。1-日，2-月，3-自定义，4-周，5-季度，6-年。"
    },
    "viewType": {
      "type": "integer",
      "enum": [1, 2],
      "description": "视角类型。1-门店视角，2-集团视角。"
    },
    "pickupSumMedhod": {
      "type": "integer",
      "enum": [1, 2, 3],
      "description": "自提统计方式。1-自提单独统计，2-自提归入外卖，3-自提归入堂食。默认 1。"
    },
    "takeoutSumMedhod": {
      "type": "integer",
      "enum": [1, 2],
      "description": "外带统计方式。1-外带单独统计，2-外带归入堂食。默认 1。"
    },
    "businessTypeList": {
      "type": ["array", "null"],
      "description": "业务类型过滤条件。",
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
    "brandIdList": {
      "type": ["array", "null"],
      "description": "品牌 ID 列表。",
      "items": {
        "type": "integer"
      }
    },
    "clientSource": {
      "type": ["string", "null"],
      "description": "客户端标识，可选。"
    },
    "shiftStatus": {
      "type": ["integer", "null"],
      "description": "是否交班。0-否，1-是。"
    },
    "isTest": {
      "type": ["integer", "null"],
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
  "description": "云助手营业指标返回结果。该接口直接返回 YzsBusinessMetricsVo，本身包含 success/code/message 等基础状态字段，不再额外包一层 data。",
  "$defs": {
    "typeSummary": {
      "type": "object",
      "description": "业务类型或渠道类型维度的营业指标明细。",
      "properties": {
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
        },
        "orderAmount": {
          "type": "number",
          "description": "营业额。"
        },
        "incUnPayOrderAmount": {
          "type": "number",
          "description": "营业额，包含待结账。"
        },
        "unPayOrderAmount": {
          "type": "number",
          "description": "待结账金额。"
        },
        "unLdTotalAmount": {
          "type": "number",
          "description": "未落单金额。"
        },
        "actualReceiptAmount": {
          "type": "number",
          "description": "营业收入。"
        },
        "discountAmount": {
          "type": "number",
          "description": "优惠金额。"
        },
        "discountRate": {
          "type": "number",
          "description": "优惠占比。"
        },
        "saleOrderNum": {
          "type": "integer",
          "description": "有效订单数。"
        },
        "disFrontDayAverage": {
          "type": "number",
          "description": "折前日均。"
        },
        "disAfterDayAverage": {
          "type": "number",
          "description": "折后日均。"
        },
        "disFrontOrderAverage": {
          "type": "number",
          "description": "折前单均。"
        },
        "disAfterOrderAverage": {
          "type": "number",
          "description": "折后单均。"
        },
        "customerNum": {
          "type": "integer",
          "description": "客流量。"
        },
        "disBeforePersonAvg": {
          "type": "number",
          "description": "折前人均。"
        },
        "disAfterPersonAvg": {
          "type": "number",
          "description": "折后人均。"
        },
        "traffic": {
          "type": "integer",
          "description": "客流量。"
        },
        "refundAmount": {
          "type": "number",
          "description": "退货金额。"
        },
        "refundOrderNum": {
          "type": "integer",
          "description": "退货单数。"
        },
        "chainActualReceiptAmountRate": {
          "type": "number",
          "description": "营业收入环比率。"
        },
        "chainOrderAmountRate": {
          "type": "number",
          "description": "营业额环比率。"
        },
        "chainIncUnPayOrderAmountRate": {
          "type": "number",
          "description": "营业额(包含待结账)环比率。"
        },
        "chainDiscountAmountRate": {
          "type": "number",
          "description": "优惠金额环比率。"
        },
        "chainCustomerNumRate": {
          "type": "number",
          "description": "客流环比率。"
        },
        "chainDisBeforePersonAvgRate": {
          "type": "number",
          "description": "折前人均环比率。"
        },
        "chainDisAfterPersonAvgRate": {
          "type": "number",
          "description": "折后人均环比率。"
        },
        "chainSaleOrderNumRate": {
          "type": "number",
          "description": "有效订单数环比率。"
        },
        "chainDisFrontOrderAverageRate": {
          "type": "number",
          "description": "折前单均环比率。"
        },
        "chainDisAfterOrderAverageRate": {
          "type": "number",
          "description": "折后单均环比率。"
        },
        "chainRefundAmountRate": {
          "type": "number",
          "description": "退货金额环比率。"
        },
        "chainRefundOrderNumRate": {
          "type": "number",
          "description": "退货单数环比率。"
        },
        "sameActualReceiptAmountRate": {
          "type": "number",
          "description": "营业收入同比率。"
        },
        "sameOrderAmountRate": {
          "type": "number",
          "description": "营业额同比率。"
        },
        "sameIncUnPayOrderAmountRate": {
          "type": "number",
          "description": "营业额(包含待结账)同比率。"
        },
        "sameDiscountAmountRate": {
          "type": "number",
          "description": "优惠金额同比率。"
        },
        "sameCustomerNumRate": {
          "type": "number",
          "description": "客流同比率。"
        },
        "sameDisBeforePersonAvgRate": {
          "type": "number",
          "description": "折前人均同比率。"
        },
        "sameDisAfterPersonAvgRate": {
          "type": "number",
          "description": "折后人均同比率。"
        },
        "sameSaleOrderNumRate": {
          "type": "number",
          "description": "有效订单数同比率。"
        },
        "sameDisFrontOrderAverageRate": {
          "type": "number",
          "description": "折前单均同比率。"
        },
        "sameDisAfterOrderAverageRate": {
          "type": "number",
          "description": "折后单均同比率。"
        },
        "sameRefundAmountRate": {
          "type": "number",
          "description": "退货金额同比率。"
        },
        "sameRefundOrderNumRate": {
          "type": "number",
          "description": "退货单数同比率。"
        },
        "takeawayActualReceiptAmountRate": {
          "type": "number",
          "description": "外卖对比全部的实收占比。"
        },
        "takeawayOrderAmountRate": {
          "type": "number",
          "description": "外卖对比全部的营业额占比。"
        },
        "takeawaySaleOrderNumRate": {
          "type": "number",
          "description": "外卖对比全部的订单占比。"
        },
        "memberNumRate": {
          "type": "number",
          "description": "客人收入构成占比。"
        },
        "memberIncomer": {
          "type": "number",
          "description": "会员收入。"
        },
        "nonmemberIncomer": {
          "type": "number",
          "description": "非会员收入。"
        },
        "memberOrderNum": {
          "type": "integer",
          "description": "会员订单数。"
        },
        "nonmemberOrderNum": {
          "type": "integer",
          "description": "非会员订单数。"
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
    "orderAmount": {
      "type": "number",
      "description": "营业额。"
    },
    "incUnPayOrderAmount": {
      "type": "number",
      "description": "营业额，包含待结账。"
    },
    "unPayOrderAmount": {
      "type": "number",
      "description": "待结账金额。"
    },
    "unLdTotalAmount": {
      "type": "number",
      "description": "未落单金额。"
    },
    "refundActualAmount": {
      "type": "number",
      "description": "退货实收金额。"
    },
    "refundAmount": {
      "type": "number",
      "description": "退货金额。"
    },
    "actualReceiptAmount": {
      "type": "number",
      "description": "营业收入。"
    },
    "discountAmount": {
      "type": "number",
      "description": "优惠金额。"
    },
    "discountRate": {
      "type": "number",
      "description": "优惠占比。"
    },
    "saleOrderNum": {
      "type": "integer",
      "description": "有效订单数。"
    },
    "refundOrderNum": {
      "type": "integer",
      "description": "退货单数。"
    },
    "disFrontDayAverage": {
      "type": "number",
      "description": "折前日均。"
    },
    "disAfterDayAverage": {
      "type": "number",
      "description": "折后日均。"
    },
    "disFrontOrderAverage": {
      "type": "number",
      "description": "折前单均。"
    },
    "disAfterOrderAverage": {
      "type": "number",
      "description": "折后单均。"
    },
    "customerNum": {
      "type": "integer",
      "description": "客流量。"
    },
    "disBeforePersonAvg": {
      "type": "number",
      "description": "折前人均。"
    },
    "disAfterPersonAvg": {
      "type": "number",
      "description": "折后人均。"
    },
    "chainActualReceiptAmountRate": {
      "type": "number",
      "description": "营业收入环比率。"
    },
    "chainOrderAmountRate": {
      "type": "number",
      "description": "营业额环比率。"
    },
    "chainIncUnPayOrderAmountRate": {
      "type": "number",
      "description": "营业额(包含待结账)环比率。"
    },
    "chainDiscountAmountRate": {
      "type": "number",
      "description": "优惠金额环比率。"
    },
    "chainCustomerNumRate": {
      "type": "number",
      "description": "客流环比率。"
    },
    "chainDisBeforePersonAvgRate": {
      "type": "number",
      "description": "折前人均环比率。"
    },
    "chainDisAfterPersonAvgRate": {
      "type": "number",
      "description": "折后人均环比率。"
    },
    "chainSaleOrderNumRate": {
      "type": "number",
      "description": "有效订单数环比率。"
    },
    "chainDisFrontOrderAverageRate": {
      "type": "number",
      "description": "折前单均环比率。"
    },
    "chainDisAfterOrderAverageRate": {
      "type": "number",
      "description": "折后单均环比率。"
    },
    "chainRefundAmountRate": {
      "type": "number",
      "description": "退货金额环比率。"
    },
    "chainRefundActualAmountRate": {
      "type": "number",
      "description": "退货实收金额环比率。"
    },
    "chainRefundOrderNumRate": {
      "type": "number",
      "description": "退货单数环比率。"
    },
    "sameActualReceiptAmountRate": {
      "type": "number",
      "description": "营业收入同比率。"
    },
    "sameOrderAmountRate": {
      "type": "number",
      "description": "营业额同比率。"
    },
    "sameIncUnPayOrderAmountRate": {
      "type": "number",
      "description": "营业额(包含待结账)同比率。"
    },
    "sameDiscountAmountRate": {
      "type": "number",
      "description": "优惠金额同比率。"
    },
    "sameCustomerNumRate": {
      "type": "number",
      "description": "客流同比率。"
    },
    "sameDisBeforePersonAvgRate": {
      "type": "number",
      "description": "折前人均同比率。"
    },
    "sameDisAfterPersonAvgRate": {
      "type": "number",
      "description": "折后人均同比率。"
    },
    "sameSaleOrderNumRate": {
      "type": "number",
      "description": "有效订单数同比率。"
    },
    "sameDisFrontOrderAverageRate": {
      "type": "number",
      "description": "折前单均同比率。"
    },
    "sameDisAfterOrderAverageRate": {
      "type": "number",
      "description": "折后单均同比率。"
    },
    "sameRefundAmountRate": {
      "type": "number",
      "description": "退货金额同比率。"
    },
    "sameRefundActualAmountRate": {
      "type": "number",
      "description": "退货实收金额同比率。"
    },
    "sameRefundOrderNumRate": {
      "type": "number",
      "description": "退货单数同比率。"
    },
    "businessTypeList": {
      "type": ["array", "null"],
      "description": "业务类型统计列表。",
      "items": {
        "$ref": "#/$defs/typeSummary"
      }
    },
    "platformTypeList": {
      "type": ["array", "null"],
      "description": "渠道类型统计列表。",
      "items": {
        "$ref": "#/$defs/typeSummary"
      }
    },
    "updateTime": {
      "type": ["string", "null"],
      "description": "数据更新时间，格式通常为 yyyy-MM-dd HH:mm:ss。"
    }
  }
}
```

调用示例:
```bash
python3 ./scripts/report_proxy.py '/report/getYzsBusinessMetrics' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"period":3,"viewType":1}'
```
