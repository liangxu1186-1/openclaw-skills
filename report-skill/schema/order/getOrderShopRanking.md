# 查询门店榜单 / 门店排行

## 接口基本信息

- 原始路径 (path): `/report/getOrderShopRanking`
- 请求方法: `POST`
- 功能描述:
  查询指定时间范围内的门店排行，按选定指标输出榜首、榜尾、合计和头部门店列表。
- 注意:
  Skill 文档中必须使用原始路径。实际请求时由 `report_proxy.py` 自动拼接 `/report/openclaw/bridge`。
  调用方不需要传 `groupId` 和 `userId`，服务端会根据 `X-OpenClaw-PublicKey` 自动补齐绑定身份。
  `metricsType` 为必填，决定门店排行的排序指标。
  当用户只说“门店榜单 / 门店排行”而未指定指标时，skill 默认按营业额榜单处理，即 `metricsType = 1`。
  服务端会强制 `queryType = 1`，并把 `limitNum` 固定为 `5`。
  当 `flag` 为空时，服务端默认按 `2-营业日` 处理。
  当 `groupKey` 为空时，服务端默认按 `1-门店` 处理。
  当 `flag = 1` 且只传 8 位日期时，服务端会自动补齐为 `yyyyMMdd000000` 到 `yyyyMMdd235959`。
  不要使用 `/report/getShopSaleRank`、`/report/shopRank` 这类错误别名路径，也不要误用 `dateType/startDate/endDate/viewType` 参数体系。
  `report_proxy.py` 会返回裁剪后的结构化结果，默认只保留 `high`、`low`、`sum`、`topStores`、`updateTime`，不会把完整榜单 `list` 整包返回给模型。

## 分析侧重点

调用本接口后，可优先从以下角度解读数据：

1. 榜首与榜尾门店差距是否过大，判断集团内经营分化是否明显。
2. 合计与头部门店占比是否过度集中，识别头部依赖风险。
3. 若按营业额或实收排序，需关注高销售但优惠占比偏高的门店。
4. 若按客流或订单量排序，需关注高流量但转化金额偏低的门店。

request:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "查询门店榜单 / 门店排行请求参数。原始路径: /report/getOrderShopRanking",
  "properties": {
    "flag": {
      "type": ["integer", "null"],
      "enum": [1, 2, 3, null],
      "description": "日期标识。1-销售日，2-营业日，3-开台日。为空时默认 2。"
    },
    "stime": {
      "type": ["integer", "string"],
      "description": "开始时间。通常传 8 位日期 yyyyMMdd；当 flag=1 时服务端会自动补齐时分秒。"
    },
    "etime": {
      "type": ["integer", "string"],
      "description": "结束时间。通常传 8 位日期 yyyyMMdd；当 flag=1 时服务端会自动补齐时分秒。"
    },
    "metricsType": {
      "type": "integer",
      "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
      "description": "排行指标。1-营业额，2-营业收入，3-优惠金额，4-折前单均，5-折后单均，6-客流，7-订单量，8-折前人均，9-折后人均，10-退货金额，11-退货单数，12-营业额（包含未支付），13-待结营业额，14-优惠占比。"
    },
    "businessType": {
      "type": ["integer", "null"],
      "description": "业务类型；与 businessTypeList 二选一或同时传递。"
    },
    "businessTypeList": {
      "type": ["array", "null"],
      "description": "业务类型列表。服务端会按业务类型合并统计。",
      "items": {
        "type": "integer"
      }
    },
    "orgList": {
      "type": ["array", "null"],
      "description": "指定门店 ID 列表。不传时服务端按当前账号权限门店范围处理。",
      "items": {
        "type": "integer"
      }
    },
    "goodsId": {
      "type": ["integer", "null"],
      "description": "商品 ID。用于商品相关排行过滤。"
    },
    "skuId": {
      "type": ["integer", "null"],
      "description": "SKU ID。用于商品相关排行过滤。"
    },
    "goodsName": {
      "type": ["string", "null"],
      "description": "商品名称模糊匹配。"
    },
    "goodsCode": {
      "type": ["string", "null"],
      "description": "商品编码。"
    },
    "goodsFlag": {
      "type": ["integer", "null"],
      "description": "商品过滤标识。服务端可能据此自动转换 goodsTypeList。"
    },
    "goodsTypeList": {
      "type": ["array", "null"],
      "description": "商品类型列表。",
      "items": {
        "type": "integer"
      }
    },
    "groupKey": {
      "type": ["integer", "null"],
      "enum": [1, null],
      "description": "分组维度。该接口当前按门店排行处理，默认 1。"
    },
    "queryType": {
      "type": ["integer", "null"],
      "description": "查询类型。服务端会强制改为 1。"
    },
    "limitNum": {
      "type": ["integer", "null"],
      "description": "榜单条数。服务端会强制改为 5。"
    },
    "isMore": {
      "type": ["integer", "null"],
      "enum": [0, 1, null],
      "description": "是否查看更多。0-否，1-是。默认 0。"
    },
    "businessFlag": {
      "type": ["integer", "null"],
      "description": "业务过滤标识。默认 2。"
    }
  },
  "required": ["metricsType", "stime", "etime"]
}
```

response:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "description": "Skill 脚本裁剪后的门店榜单结果。原始服务返回 ShopRankingSumVo，但 report_proxy.py 默认只保留轻量结构。",
  "$defs": {
    "store": {
      "type": "object",
      "properties": {
        "orgId": {
          "type": ["integer", "null"],
          "description": "门店 ID。"
        },
        "orgName": {
          "type": ["string", "null"],
          "description": "门店名称。"
        },
        "orderAmount": {
          "type": ["number", "null"],
          "description": "营业额。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "营业收入 / 实收金额。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额。"
        },
        "traffic": {
          "type": ["integer", "null"],
          "description": "客流。"
        },
        "orderCount": {
          "type": ["integer", "null"],
          "description": "订单量。"
        },
        "refundAmount": {
          "type": ["number", "null"],
          "description": "退货金额。"
        },
        "discountRate": {
          "type": ["number", "null"],
          "description": "优惠占比。"
        }
      }
    }
  },
  "properties": {
    "request": {
      "type": "object",
      "description": "脚本保留的关键请求参数回显。",
      "properties": {
        "metricsType": {
          "type": ["integer", "null"],
          "description": "排行指标。"
        },
        "flag": {
          "type": ["integer", "null"],
          "description": "日期标识。"
        },
        "stime": {
          "type": ["integer", "string", "null"],
          "description": "开始时间。"
        },
        "etime": {
          "type": ["integer", "string", "null"],
          "description": "结束时间。"
        },
        "businessType": {
          "type": ["integer", "null"],
          "description": "业务类型。"
        },
        "businessTypeList": {
          "type": ["array", "null"],
          "description": "业务类型列表。",
          "items": {
            "type": "integer"
          }
        },
        "goodsId": {
          "type": ["integer", "null"],
          "description": "商品 ID。"
        },
        "skuId": {
          "type": ["integer", "null"],
          "description": "SKU ID。"
        }
      }
    },
    "high": {
      "$ref": "#/$defs/store",
      "description": "榜首门店。"
    },
    "low": {
      "$ref": "#/$defs/store",
      "description": "榜尾门店。"
    },
    "sum": {
      "type": "object",
      "description": "合计行，仅保留核心指标。",
      "properties": {
        "orderAmount": {
          "type": ["number", "null"],
          "description": "营业额合计。"
        },
        "actualReceiptAmount": {
          "type": ["number", "null"],
          "description": "营业收入 / 实收金额合计。"
        },
        "discountAmount": {
          "type": ["number", "null"],
          "description": "优惠金额合计。"
        },
        "traffic": {
          "type": ["integer", "null"],
          "description": "客流合计。"
        },
        "orderCount": {
          "type": ["integer", "null"],
          "description": "订单量合计。"
        },
        "refundAmount": {
          "type": ["number", "null"],
          "description": "退货金额合计。"
        },
        "discountRate": {
          "type": ["number", "null"],
          "description": "优惠占比。"
        }
      }
    },
    "topStores": {
      "type": "array",
      "description": "脚本裁剪后的头部门店列表，默认不返回完整榜单明细。",
      "items": {
        "$ref": "#/$defs/store"
      }
    },
    "updateTime": {
      "type": ["string", "null"],
      "description": "数据更新时间。"
    }
  }
}
```

请求示例:
```json
{
  "flag": 2,
  "stime": 20260301,
  "etime": 20260307,
  "metricsType": 1,
  "businessTypeList": [1, 2]
}
```

`report_proxy.py` 调用示例:
```bash
python3 scripts/report_proxy.py \
  --base-url http://127.0.0.1:8087 \
  --api-path /report/getOrderShopRanking \
  --method POST \
  --payload '{"flag":2,"stime":20260301,"etime":20260307,"metricsType":1,"businessTypeList":[1,2]}'
```
