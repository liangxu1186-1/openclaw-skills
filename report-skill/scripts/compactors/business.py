from compactors.common import TOP_LIMIT, pick_fields, sort_desc


def compact_business_metrics(result, payload):
    if not isinstance(result, dict):
        return result

    summary = pick_fields(
        result,
        [
            "success",
            "code",
            "message",
            "updateTime",
            "orderAmount",
            "actualReceiptAmount",
            "discountAmount",
            "refundAmount",
            "refundActualAmount",
            "saleOrderNum",
            "customerNum",
            "traffic",
            "discountRate",
            "disFrontOrderAverage",
            "disAfterOrderAverage",
            "disBeforePersonAvg",
            "disAfterPersonAvg",
        ],
    )
    request_summary = pick_fields(payload or {}, ["flag", "stime", "etime", "period", "viewType"])
    if request_summary:
        summary["request"] = request_summary
    return summary


def compact_goods_summary(result, payload):
    categories = result if isinstance(result, list) else None
    if categories is None and isinstance(result, dict):
        for key in ("list", "rows", "data", "result"):
            if isinstance(result.get(key), list):
                categories = result[key]
                break
    if not isinstance(categories, list):
        return result

    normalized_categories = []
    goods_rows = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        category_name = category.get("offlineCategoryName") or "未命名分类"
        normalized_categories.append(
            {
                "offlineCategoryName": category_name,
                "actualReceiptAmount": category.get("actualReceiptAmount"),
                "orderAmount": category.get("orderAmount"),
                "saleGoodsNum": category.get("saleGoodsNum"),
            }
        )
        for goods in category.get("goodsPosCateSaleSummaryVos") or []:
            if not isinstance(goods, dict):
                continue
            goods_rows.append(
                {
                    "goodsName": goods.get("goodsName") or "未命名商品",
                    "categoryName": category_name,
                    "actualReceiptAmount": goods.get("actualReceiptAmount"),
                    "orderAmount": goods.get("orderAmount"),
                    "saleGoodsNum": goods.get("saleGoodsNum"),
                }
            )

    return {
        "request": pick_fields(payload or {}, ["viewType", "dateType", "startDate", "endDate", "goodsFlag"]),
        "categoryCount": len(normalized_categories),
        "topCategoriesByReceipt": sort_desc(normalized_categories, "actualReceiptAmount")[:TOP_LIMIT],
        "topGoodsByReceipt": sort_desc(goods_rows, "actualReceiptAmount")[:TOP_LIMIT],
        "topGoodsBySales": sort_desc(goods_rows, "saleGoodsNum")[:TOP_LIMIT],
    }
