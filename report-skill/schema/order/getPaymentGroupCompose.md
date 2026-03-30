# 查询支付分组构成、支付科目构成

## 接口基本信息

- 原始路径 (path): `/report/getPaymentGroupCompose`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的支付分组构成和支付科目构成，返回整体交易笔数、实收金额、会员现金卡值、礼品卡消费、会员储值收款，以及按支付分组展开的支付科目明细。
- 注意:
  Skill 文档中必须使用原始路径。实际发起请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 绑定身份自动补齐。
  当 `period` 为空时，服务端会默认按 `1-日` 处理。
  当 `period = 2` 时，服务端会自动把 `stime` 和 `etime` 展开为整月范围。
  当 `flag = 1` 且时间只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  `isSaleConStore` 默认 `false`，即默认不把会员现金卡值相关支付科目 `30010001`、`30010002`、`30010009` 计入支付分组明细，并同时排除业务类型 `5`、`11` 的储值收入。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 哪些支付分组贡献最高，包括交易笔数和实收金额的头部来源。
2. 哪些支付分组下的支付科目高度集中，判断收入是否过度依赖少数支付方式。
3. 会员现金卡值、礼品卡消费、会员储值收款对整体支付结构的影响是否明显。
4. 是否存在交易笔数不高但金额异常高的支付分组或支付科目，需要重点提醒。
5. 如果不同支付分组之间金额或笔数结构明显不协调，可以提示用户进一步核对支付口径或对账规则。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询支付分组构成、支付科目构成请求参数。原始路径: /report/getPaymentGroupCompose",
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
    "viewType": {
      "type": ["integer", "null"],
      "enum": [1, 2, null],
      "description": "视角类型。1-门店视角，2-集团视角。"
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
    },
    "isSaleConStore": {
      "type": ["boolean", "null"],
      "description": "会员储值是否计入支付分组构成。默认 false。"
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
  "description": "支付分组构成、支付科目构成返回结果。该接口直接返回 PaymentGroupComposeVo，本身包含 success/code/message 等基础状态字段，不再额外包一层 data。",
  "$defs": {
    "paymentSubject": {
      "type": "object",
      "description": "支付科目明细。",
      "properties": {
        "paySubjectName": {
          "type": ["string", "null"],
          "description": "支付科目名称。"
        },
        "paySubjectCode": {
          "type": ["string", "null"],
          "description": "支付科目编码。"
        },
        "orderNum": {
          "type": ["integer", "null"],
          "description": "交易笔数。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "实收金额。"
        }
      }
    },
    "paymentSubjectGroup": {
      "type": "object",
      "description": "支付分组汇总。",
      "properties": {
        "paySubjectGroupName": {
          "type": ["string", "null"],
          "description": "支付分组名称。"
        },
        "paySubjectGroupCode": {
          "type": ["string", "null"],
          "description": "支付分组编码。"
        },
        "orderNum": {
          "type": ["integer", "null"],
          "description": "该支付分组下的交易笔数。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "该支付分组下的实收金额。"
        },
        "subjectVoList": {
          "type": ["array", "null"],
          "description": "该支付分组下的支付科目明细。",
          "items": {
            "$ref": "#/$defs/paymentSubject"
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
    "orderNum": {
      "type": ["integer", "null"],
      "description": "整体交易笔数。"
    },
    "actualReceiptAmount": {
      "type": ["number", "null"],
      "description": "整体实收金额。"
    },
    "vipSaleAmount": {
      "type": ["number", "null"],
      "description": "会员现金卡值金额，对应支付科目 `30010001`、`30010002` 的汇总。"
    },
    "giftCardSaleAmount": {
      "type": ["number", "null"],
      "description": "礼品卡消费金额，对应支付科目 `30010009` 的汇总。"
    },
    "storeAmount": {
      "type": ["number", "null"],
      "description": "会员储值收款金额，对应业务类型 `5`、`11` 的汇总。"
    },
    "groupVoList": {
      "type": ["array", "null"],
      "description": "支付分组列表，每个分组下再展开支付科目明细。",
      "items": {
        "$ref": "#/$defs/paymentSubjectGroup"
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
  "shiftStatus": 0,
  "isSaleConStore": false
}
```

脚本调用示例:

```bash
python3 ./scripts/report_proxy.py '/report/getPaymentGroupCompose' '{"orgId":20001,"flag":2,"stime":20260301,"etime":20260307,"shiftStatus":0,"isSaleConStore":false}'
```
