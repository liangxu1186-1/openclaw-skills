from compactors.common import TOP_LIMIT, build_named_rows, compact_rank_summary, limit_items, pick_fields, sort_desc


def compact_order_business_daily(result, payload):
    if not isinstance(result, dict):
        return result

    return {
        "request": pick_fields(payload or {}, ["flag", "stime", "etime", "viewType", "businessTypeList", "platformTypeList"]),
        "summary": pick_fields(
            result,
            [
                "orderAmount",
                "actualReceiptAmount",
                "discountAmount",
                "refundAmount",
                "saleOrderNum",
                "customerNum",
                "disFrontOrderAverage",
                "disAfterOrderAverage",
            ],
        ),
        "topBusinessTypesByReceipt": build_named_rows(
            result.get("businessTypeSummaryVoList"),
            ["businessTypeName", "orderNum", "actualReceiptAmount", "orderAverage", "businessTypeRate"],
            "actualReceiptAmount",
        ),
    }


def compact_header_report(result, payload, request_fields):
    if not isinstance(result, dict):
        return result

    metric_fields = [
        "orderAmount",
        "orderAmountRate",
        "actualReceiptAmount",
        "actualReceiptAmountRate",
        "discountAmount",
        "discountAmountRate",
        "saleOrderNum",
        "saleOrderNumRate",
        "customerNum",
        "disFrontOrderAverage",
        "disAfterOrderAverage",
        "disBeforePersonAvg",
        "disAfterPersonAvg",
    ]
    rows = result.get("list") or result.get("rows") or []
    return {
        "request": pick_fields(payload or {}, request_fields),
        "size": result.get("size"),
        "sum": pick_fields(result.get("sum") or {}, metric_fields),
        "topRows": build_named_rows(rows, metric_fields, "orderAmount"),
        "headCount": len(result.get("headList") or []),
    }


def compact_payment_group_compose(result, payload):
    if not isinstance(result, dict):
        return result

    top_groups = []
    for group in sort_desc(result.get("groupVoList") or [], "actualReceiptAmount")[:TOP_LIMIT]:
        if not isinstance(group, dict):
            continue
        top_groups.append(
            {
                **pick_fields(group, ["paySubjectGroupName", "paySubjectGroupCode", "orderNum", "actualReceiptAmount"]),
                "topSubjects": build_named_rows(
                    group.get("subjectVoList"),
                    ["paySubjectName", "paySubjectCode", "orderNum", "actualReceiptAmount"],
                    "actualReceiptAmount",
                )[:3],
            }
        )

    return {
        "request": pick_fields(payload or {}, ["flag", "stime", "etime", "viewType", "isSaleConStore"]),
        "summary": pick_fields(
            result,
            ["orderNum", "actualReceiptAmount", "vipSaleAmount", "giftCardSaleAmount", "storeAmount"],
        ),
        "topGroups": top_groups,
    }


def compact_order_shop_ranking(result, payload):
    if not isinstance(result, dict):
        return result

    item_fields = [
        "orgId",
        "orgName",
        "orderAmount",
        "actualReceiptAmount",
        "discountAmount",
        "traffic",
        "orderCount",
        "refundAmount",
        "discountRate",
    ]

    return {
        "request": pick_fields(
            payload or {},
            ["metricsType", "flag", "stime", "etime", "businessType", "businessTypeList", "goodsId", "skuId"],
        ),
        "high": pick_fields(result.get("high") or {}, item_fields),
        "low": pick_fields(result.get("low") or {}, item_fields),
        "sum": pick_fields(
            result.get("sum") or {},
            ["orderAmount", "actualReceiptAmount", "discountAmount", "traffic", "orderCount", "refundAmount", "discountRate"],
        ),
        "topStores": limit_items(
            sort_desc([pick_fields(item, item_fields) for item in result.get("list") or [] if isinstance(item, dict)], "orderAmount")
        ),
        "updateTime": result.get("updateTime"),
    }


def build_order_registry():
    return {
        "/report/orderBusinessDaily": lambda payload, result: compact_order_business_daily(result, payload),
        "/report/getOrderDimensionStatsList": lambda payload, result: compact_header_report(
            result, payload, ["dimensions", "groupKey", "metrics", "flag", "stime", "etime", "period"]
        ),
        "/report/getOrderIncomeStatsList": lambda payload, result: compact_header_report(
            result, payload, ["groupKey", "metrics", "flag", "stime", "etime", "period"]
        ),
        "/report/getPaymentGroupCompose": lambda payload, result: compact_payment_group_compose(result, payload),
        "/report/salePeriodSummary": lambda payload, result: compact_header_report(
            result,
            payload,
            ["viewType", "dateType", "startDate", "endDate", "periodMethod", "periodType", "statisticsDimension", "columns"],
        ),
        "/report/getOrderShopRanking": lambda payload, result: compact_order_shop_ranking(result, payload),
    }
