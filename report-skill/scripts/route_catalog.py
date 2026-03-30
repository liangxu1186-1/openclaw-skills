import difflib


SUPPORTED_ROUTE_CATALOG = {
    "/report/getYzsBusinessMetrics": {
        "category": "business",
        "doc": "./api/business.md",
    },
    "/report/getOrderIncomeStatsList": {
        "category": "goods",
        "doc": "./api/goods.md",
    },
    "/report/goodsPosCateSaleSummary": {
        "category": "goods",
        "doc": "./api/goods.md",
    },
    "/report/goodsSaleSummary": {
        "category": "goods",
        "doc": "./api/goods.md",
    },
    "/report/overviewGoodsSummary": {
        "category": "goods",
        "doc": "./api/goods.md",
    },
    "/report/scrm/member/customerPeriodSummary": {
        "category": "member",
        "doc": "./api/member.md",
    },
    "/report/scrm/member/customerTotalSummary": {
        "category": "member",
        "doc": "./api/member.md",
    },
    "/report/memberLikeSummary": {
        "category": "member",
        "doc": "./api/member.md",
    },
    "/report/scrm/member/orgOpenCardMemberSummary": {
        "category": "member",
        "doc": "./api/member.md",
    },
    "/report/scrm/member/orgRechargeMemberSummary": {
        "category": "member",
        "doc": "./api/member.md",
    },
    "/report/getOrderDimensionStatsList": {
        "category": "order",
        "doc": "./api/order.md",
    },
    "/report/getOrderShopRanking": {
        "category": "order",
        "doc": "./api/order.md",
        "forced_payload": {"period": 3},
    },
    "/report/getPaymentGroupCompose": {
        "category": "order",
        "doc": "./api/order.md",
    },
    "/report/orderBusinessDaily": {
        "category": "order",
        "doc": "./api/order.md",
    },
    "/report/salePeriodSummary": {
        "category": "order",
        "doc": "./api/order.md",
    },
}

CATEGORY_KEYWORDS = {
    "member": ("member", "scrm", "customer", "card", "recharge", "like"),
    "order": ("order", "shop", "rank", "payment", "sale"),
    "goods": ("goods", "cate", "item"),
    "business": ("business", "metrics", "income", "turnover"),
}


def default_normalize_api_path(api_path):
    if not api_path:
        raise ValueError("path 不能为空")
    return api_path if api_path.startswith("/") else "/" + api_path


def get_supported_route(api_path, normalize_path=None):
    normalizer = normalize_path or default_normalize_api_path
    normalized_path = normalizer(api_path)
    return normalized_path, SUPPORTED_ROUTE_CATALOG.get(normalized_path)


def infer_route_category(normalized_path):
    lowered = normalized_path.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                return category
    return ""


def suggest_supported_routes(api_path, normalize_path=None, limit=5):
    normalizer = normalize_path or default_normalize_api_path
    normalized_path = normalizer(api_path)
    all_routes = list(SUPPORTED_ROUTE_CATALOG.keys())
    suggestions = []
    inferred_category = infer_route_category(normalized_path)

    if inferred_category:
        for candidate, meta in SUPPORTED_ROUTE_CATALOG.items():
            if meta["category"] == inferred_category and candidate not in suggestions:
                suggestions.append(candidate)
            if len(suggestions) >= limit:
                return suggestions

    for candidate in difflib.get_close_matches(normalized_path, all_routes, n=limit, cutoff=0.25):
        if candidate not in suggestions:
            suggestions.append(candidate)

    for candidate in all_routes:
        if candidate not in suggestions:
            suggestions.append(candidate)
        if len(suggestions) >= limit:
            return suggestions

    return suggestions


def validate_supported_path(api_path, normalize_path=None):
    normalized_path, route_config = get_supported_route(api_path, normalize_path=normalize_path)
    if route_config is not None:
        return normalized_path

    suggestions = suggest_supported_routes(normalized_path, normalize_path=lambda value: value)
    doc_hint = "./api/order.md"
    if suggestions:
        first_meta = SUPPORTED_ROUTE_CATALOG.get(suggestions[0], {})
        doc_hint = first_meta.get("doc", doc_hint)
    inferred_category = infer_route_category(normalized_path)
    if inferred_category:
        for meta in SUPPORTED_ROUTE_CATALOG.values():
            if meta["category"] == inferred_category:
                doc_hint = meta.get("doc", doc_hint)
                break

    raise ValueError(
        f"不支持的接口路径: {normalized_path}。"
        f" 只允许调用 report-skill 已登记接口。"
        f" 可用候选接口: {', '.join(suggestions)}。"
        f" 先查看 {doc_hint}。"
    )
