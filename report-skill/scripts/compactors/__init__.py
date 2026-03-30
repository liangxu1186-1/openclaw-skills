from compactors.business import compact_business_metrics, compact_goods_summary
from compactors.common import default_normalize_api_path
from compactors.member import build_member_registry
from compactors.order import build_order_registry


COMPACTOR_REGISTRY = {
    "/report/getYzsBusinessMetrics": lambda payload, result: compact_business_metrics(result, payload),
    "/report/goodsPosCateSaleSummary": lambda payload, result: compact_goods_summary(result, payload),
    **build_order_registry(),
    **build_member_registry(),
}


def compact_result(api_path, payload, result, normalize_path=None):
    normalizer = normalize_path or default_normalize_api_path
    normalized_path = normalizer(api_path)
    compactor = COMPACTOR_REGISTRY.get(normalized_path)
    if compactor is None:
        return result
    return compactor(payload, result)
