import difflib


COMMON_REQUIRED_FIELDS = ("startTime", "endTime", "flag")
COMMON_FORBIDDEN_FIELDS = (
    "stime",
    "etime",
    "dateType",
    "startDate",
    "endDate",
    "period",
    "viewType",
    "metricsType",
    "summaryGoodsType",
    "sortType",
    "dataNum",
    "queryType",
    "limitNum",
)


def build_agent_route(category, doc, hint):
    return {
        "category": category,
        "doc": doc,
        "payload_contract": {
            "family": "startTime/endTime/flag",
            "required_fields": COMMON_REQUIRED_FIELDS,
            "forbidden_fields": COMMON_FORBIDDEN_FIELDS,
            "hint": hint,
        },
    }


SUPPORTED_ROUTE_CATALOG = {
    "/agent/order/overview": build_agent_route("order", "./api/order.md", "订单总览接口只传 startTime/endTime/flag。"),
    "/agent/order/business-type": build_agent_route("order", "./api/order.md", "订单业务类型接口只传 startTime/endTime/flag。"),
    "/agent/order/channel-type": build_agent_route("order", "./api/order.md", "订单渠道类型接口只传 startTime/endTime/flag。"),
    "/agent/order/refund": build_agent_route("order", "./api/order.md", "订单退款接口只传 startTime/endTime/flag。"),
    "/agent/order/shop-ranking": build_agent_route("order", "./api/order.md", "门店榜单接口只传 startTime/endTime/flag。"),
    "/agent/order/meal-period": build_agent_route("order", "./api/order.md", "订单餐段接口只传 startTime/endTime/flag。"),
    "/agent/order/time-period": build_agent_route("order", "./api/order.md", "订单时段接口只传 startTime/endTime/flag。"),
    "/agent/order/cashier-income": build_agent_route("order", "./api/order.md", "收银员收款统计接口只传 startTime/endTime/flag。"),
    "/agent/goods/overview": build_agent_route("goods", "./api/goods.md", "商品总览接口只传 startTime/endTime/flag。"),
    "/agent/goods/sales-ranking": build_agent_route("goods", "./api/goods.md", "商品销售排行接口只传 startTime/endTime/flag。"),
    "/agent/goods/category-ranking": build_agent_route("goods", "./api/goods.md", "商品分类排行接口只传 startTime/endTime/flag。"),
    "/agent/goods/refund-ranking": build_agent_route("goods", "./api/goods.md", "商品退货排行接口只传 startTime/endTime/flag。"),
    "/agent/goods/gift-ranking": build_agent_route("goods", "./api/goods.md", "商品赠送排行接口只传 startTime/endTime/flag。"),
    "/agent/goods/income-subject": build_agent_route("goods", "./api/goods.md", "商品收入科目统计接口只传 startTime/endTime/flag。"),
    "/agent/payment/compose": build_agent_route("payment", "./api/payment.md", "支付构成接口只传 startTime/endTime/flag。"),
    "/agent/payment/discount-overview": build_agent_route("payment", "./api/payment.md", "支付优惠接口只传 startTime/endTime/flag。"),
    "/agent/marketing/promotion-summary": build_agent_route("marketing", "./api/marketing.md", "促销活动汇总接口只传 startTime/endTime/flag。"),
    "/agent/marketing/activity-summary": build_agent_route("marketing", "./api/marketing.md", "营销活动汇总接口只传 startTime/endTime/flag。"),
    "/agent/member/overview": build_agent_route("member", "./api/member.md", "会员总览接口只传 startTime/endTime/flag。"),
    "/agent/member/preference": build_agent_route("member", "./api/member.md", "会员偏好接口只传 startTime/endTime/flag。"),
}

CATEGORY_KEYWORDS = {
    "order": ("order", "shop", "cashier", "refund", "ranking", "overview", "period", "channel", "business"),
    "goods": ("goods", "category", "gift", "refund", "ranking", "overview", "period", "income", "subject"),
    "payment": ("payment", "discount", "subject", "category", "compose"),
    "marketing": ("marketing", "promotion", "campaign", "activity"),
    "member": ("member", "preference", "favorite", "like", "overview", "store"),
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
    raise ValueError(
        f"不支持的接口路径: {normalized_path}。"
        f" 只允许调用 report-skill 已登记接口。"
        f" 可用候选接口: {', '.join(suggestions)}。"
        f" 先查看 ./api/agent.md。"
    )


def get_payload_contract(api_path, normalize_path=None):
    _, route_config = get_supported_route(api_path, normalize_path=normalize_path)
    if route_config is None:
        return None
    return route_config.get("payload_contract")
