import argparse
import base64
import json
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

import requests

BRIDGE_PROXY_PATH = "/report/openclaw/bridge"
PUBLIC_KEY_HEADER = "X-OpenClaw-PublicKey"
TARGET_PATH_PARAM = "targetPath"
PUBLIC_KEY_FIELD = "publicKey"
PAYLOAD_FIELD = "payload"
QUERY_FIELD = "query"
METHOD_FIELD = "method"
DEFAULT_TIMEOUT = 10
DEFAULT_STATE_DIR = "~/.openclaw"
DEFAULT_SAAS_API_URL = "https://test-shop-kaci.shouqianba.com"
TOP_LIMIT = 10


def normalize_api_path(api_path):
    if not api_path:
        raise ValueError("path 不能为空")
    return api_path if api_path.startswith("/") else "/" + api_path


def build_bridge_url(base_url):
    return base_url.rstrip("/") + BRIDGE_PROXY_PATH


def parse_json_arg(raw_value, field_name):
    if not raw_value:
        return None
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} 必须是合法 JSON") from exc


def serialize_json_value(value):
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_bridge_payload(method, payload, query, api_path, public_key):
    return {
        TARGET_PATH_PARAM: normalize_api_path(api_path),
        PUBLIC_KEY_FIELD: public_key,
        METHOD_FIELD: method,
        PAYLOAD_FIELD: serialize_json_value(payload),
        QUERY_FIELD: serialize_json_value(query),
    }


def extract_business_result(response_json):
    if isinstance(response_json, dict) and response_json.get("success") and "data" in response_json:
        return response_json["data"]
    return response_json


def to_number(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return None
    return None


def sort_desc(items, key):
    return sorted(items, key=lambda item: to_number(item.get(key)) or 0, reverse=True)


def pick_fields(payload, fields):
    return {field: payload[field] for field in fields if field in payload and payload[field] is not None}


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

    summary = {
        "request": pick_fields(payload or {}, ["viewType", "dateType", "startDate", "endDate", "goodsFlag"]),
        "categoryCount": len(normalized_categories),
        "topCategoriesByReceipt": sort_desc(normalized_categories, "actualReceiptAmount")[:TOP_LIMIT],
        "topGoodsByReceipt": sort_desc(goods_rows, "actualReceiptAmount")[:TOP_LIMIT],
        "topGoodsBySales": sort_desc(goods_rows, "saleGoodsNum")[:TOP_LIMIT],
    }
    return summary


def compact_member_period_summary(result, payload):
    if not isinstance(result, dict):
        return result

    return {
        "request": pick_fields(payload or {}, ["flag", "stime", "etime", "period", "viewType"]),
        "current": pick_fields(
            result,
            [
                "customerCount",
                "memberCount",
                "consumeMemberCount",
                "rechargeMemberCount",
                "orderAmount",
                "orderNum",
                "totalRechargeAmount",
                "totalConsumeBalanceAmount",
                "totalSedimentaryAmount",
            ],
        ),
        "previous": {
            "customerCount": result.get("upCustomerCount"),
            "memberCount": result.get("upMemberCount"),
            "consumeMemberCount": result.get("upConsumeMemberCount"),
            "rechargeMemberCount": result.get("upRechargeMemberCount"),
            "orderAmount": result.get("upOrderAmount"),
            "orderNum": result.get("upOrderNum"),
        },
        "rates": pick_fields(
            result,
            [
                "chainCustomerRate",
                "chainMemberRate",
                "chainConsumeCountRate",
                "chainRechargeAmountRate",
                "chainTotalConsumeBalanceAmountRate",
                "chainTotalSedimentaryAmountRate",
            ],
        ),
    }


def compact_result(api_path, payload, result):
    normalized_path = normalize_api_path(api_path)
    if normalized_path == "/report/getYzsBusinessMetrics":
        return compact_business_metrics(result, payload)
    if normalized_path == "/report/goodsPosCateSaleSummary":
        return compact_goods_summary(result, payload)
    if normalized_path == "/report/scrm/member/customerPeriodSummary":
        return compact_member_period_summary(result, payload)
    return result


def get_state_dir():
    state_dir = os.getenv("OPENCLAW_STATE_DIR", DEFAULT_STATE_DIR)
    return Path(state_dir).expanduser()


def load_json_file(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def base64url_no_padding(raw_bytes):
    return base64.urlsafe_b64encode(raw_bytes).decode("ascii").rstrip("=")


def public_key_from_paired(state_dir):
    paired_path = state_dir / "devices" / "paired.json"
    payload = load_json_file(paired_path)
    if not isinstance(payload, dict):
        return ""

    for device in payload.values():
        if not isinstance(device, dict):
            continue
        if device.get("clientId") == "cli" and device.get("publicKey"):
            return str(device["publicKey"]).strip()

    return ""


def public_key_from_identity(state_dir):
    identity_path = state_dir / "identity" / "device.json"
    payload = load_json_file(identity_path)
    if not isinstance(payload, dict):
        return ""

    public_key_pem = str(payload.get("publicKeyPem", "")).strip()
    if not public_key_pem:
        return ""

    pem_body = "".join(
        line.strip()
        for line in public_key_pem.splitlines()
        if "BEGIN PUBLIC KEY" not in line and "END PUBLIC KEY" not in line
    )
    if not pem_body:
        return ""

    try:
        der = base64.b64decode(pem_body)
    except Exception as exc:
        raise RuntimeError("OpenClaw publicKeyPem 解析失败") from exc

    if len(der) < 32:
        raise RuntimeError("OpenClaw publicKeyPem 内容异常")

    return base64url_no_padding(der[-32:])


def resolve_public_key():
    public_key = os.getenv("OPENCLAW_PUBLIC_KEY", "").strip()
    if public_key:
        return public_key

    state_dir = get_state_dir()
    public_key = public_key_from_paired(state_dir)
    if public_key:
        return public_key

    public_key = public_key_from_identity(state_dir)
    if public_key:
        return public_key

    raise RuntimeError("无法自动获取 OpenClaw 公钥，请检查 ~/.openclaw 状态目录或显式配置 OPENCLAW_PUBLIC_KEY")


def main():
    parser = argparse.ArgumentParser(description="通过 OpenClaw bridge 调用 SaaS 报表接口")
    parser.add_argument("path", help="原始业务路径，例如 /report/getYzsBusinessMetrics")
    parser.add_argument("payload", nargs="?", default="", help="请求体 JSON 字符串")
    parser.add_argument(
        "--method",
        default="POST",
        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
        help="HTTP 方法，默认 POST",
    )
    parser.add_argument(
        "--query",
        default="",
        help="查询参数 JSON 字符串，例如 '{\"traceId\":\"demo\"}'",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="请求超时时间，单位秒，默认 10",
    )
    args = parser.parse_args()

    base_url = os.getenv("SAAS_API_URL", DEFAULT_SAAS_API_URL).rstrip("/")
    public_key = resolve_public_key()

    if not base_url:
        raise RuntimeError("SAAS_API_URL 未配置，且默认 SaaS API 地址为空")

    payload = parse_json_arg(args.payload, "payload")
    query = parse_json_arg(args.query, "query")
    url = build_bridge_url(base_url)
    bridge_payload = build_bridge_payload(args.method, payload, query, args.path, public_key)

    response = requests.post(
        url=url,
        headers={
            "Content-Type": "application/json",
            PUBLIC_KEY_HEADER: public_key,
        },
        timeout=args.timeout,
        json=bridge_payload,
    )
    response.raise_for_status()

    try:
        result = extract_business_result(response.json())
    except ValueError:
        print(response.text)
        return

    result = compact_result(args.path, payload, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
