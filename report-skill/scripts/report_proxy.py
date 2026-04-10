import argparse
import json
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

import requests
from route_catalog import get_payload_contract, validate_supported_path

BRIDGE_PROXY_PATH = "/report/openclaw/bridge"
IDENTITY_HEADER = "X-OpenClaw-PublicKey"
TARGET_PATH_PARAM = "targetPath"
IDENTITY_FIELD = "publicKey"
PAYLOAD_FIELD = "payload"
QUERY_FIELD = "query"
METHOD_FIELD = "method"
DEFAULT_TIMEOUT = 10
DEFAULT_STATE_DIR = "~/.openclaw"
DEFAULT_AGENT_IDENTITY_PATH = Path("/home/gem/workspace/agent/identity/device.json")
DEFAULT_AGENT_CONFIG_PATH = Path("/home/gem/workspace/agent/openclaw.json")
DEFAULT_SAAS_API_URL = "https://shop-kaci.shouqianba.com"
DEFAULT_FLAG = 2
MAX_RANGE_DAYS = 90
PRIMARY_IDENTITY_ENV = "OPENCLAW_IDENTITY"


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


def build_error_result(code, message, *, error_type="runtime_error", api_path=None, detail=None):
    result = {
        "success": False,
        "code": code,
        "errorType": error_type,
        "message": message,
    }
    if api_path:
        result["path"] = api_path
    if detail is not None:
        result["detail"] = detail
    return result


def is_missing_value(value):
    return value in (None, "", [], {})


def validate_payload_contract(api_path, payload):
    if payload is None or not isinstance(payload, dict):
        return

    contract = get_payload_contract(api_path, normalize_path=normalize_api_path)
    if not contract:
        return

    forbidden_fields = sorted(
        field for field in contract.get("forbidden_fields", ()) if not is_missing_value(payload.get(field))
    )
    missing_fields = sorted(
        field for field in contract.get("required_fields", ()) if is_missing_value(payload.get(field))
    )
    if not forbidden_fields and not missing_fields:
        return

    detail = {
        "family": contract.get("family", ""),
        "requiredFields": list(contract.get("required_fields", ())),
    }
    if forbidden_fields:
        detail["forbiddenFields"] = forbidden_fields
    if missing_fields:
        detail["missingFields"] = missing_fields

    hint = contract.get("hint", "").strip()
    problems = []
    if forbidden_fields:
        problems.append(f"检测到错误参数: {', '.join(forbidden_fields)}")
    if missing_fields:
        problems.append(f"缺少必填参数: {', '.join(missing_fields)}")
    if hint:
        problems.append(hint)

    raise ValueError(
        json.dumps(
            build_error_result(
                "PAYLOAD_VALIDATION_ERROR",
                "；".join(problems),
                error_type="payload_validation",
                api_path=api_path,
                detail=detail,
            ),
            ensure_ascii=False,
        )
    )


def validate_date_range(api_path, payload):
    if payload is None or not isinstance(payload, dict):
        return

    start_time = payload.get("startTime")
    end_time = payload.get("endTime")
    if is_missing_value(start_time) or is_missing_value(end_time):
        return

    start_date = datetime.strptime(str(start_time), "%Y%m%d").date()
    end_date = datetime.strptime(str(end_time), "%Y%m%d").date()
    if (end_date - start_date).days <= MAX_RANGE_DAYS:
        return

    raise ValueError(
        json.dumps(
            build_error_result(
                "PAYLOAD_VALIDATION_ERROR",
                f"查询范围不能超过{MAX_RANGE_DAYS}天",
                error_type="payload_validation",
                api_path=api_path,
                detail={"maxRangeDays": MAX_RANGE_DAYS},
            ),
            ensure_ascii=False,
        )
    )


def normalize_payload(api_path, payload):
    if not isinstance(payload, dict):
        return payload

    normalized_path = validate_supported_path(api_path, normalize_path=normalize_api_path)
    normalized_payload = dict(payload)
    if is_missing_value(normalized_payload.get("flag")):
        normalized_payload["flag"] = DEFAULT_FLAG
    validate_payload_contract(normalized_path, normalized_payload)
    validate_date_range(normalized_path, normalized_payload)
    return normalized_payload


def build_bridge_payload(method, payload, query, api_path, identity_value):
    return {
        TARGET_PATH_PARAM: validate_supported_path(api_path, normalize_path=normalize_api_path),
        IDENTITY_FIELD: identity_value,
        METHOD_FIELD: method,
        PAYLOAD_FIELD: serialize_json_value(payload),
        QUERY_FIELD: serialize_json_value(query),
    }


def extract_business_result(response_json):
    if isinstance(response_json, dict) and response_json.get("success") and "data" in response_json:
        return response_json["data"]
    return response_json


def get_state_dir():
    state_dir = os.getenv("OPENCLAW_STATE_DIR", DEFAULT_STATE_DIR)
    return Path(state_dir).expanduser()


def load_json_file(path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_identity_value(value):
    if value is None or isinstance(value, (dict, list, tuple, set, bool)):
        return ""
    return str(value).strip()


def identity_value_from_device_file(identity_path):
    payload = load_json_file(identity_path)
    if not isinstance(payload, dict):
        return ""
    return normalize_identity_value(payload.get("deviceId"))


def identity_value_from_cloud_config(config_path):
    payload = load_json_file(config_path)
    if not isinstance(payload, dict):
        return ""

    feishu_config = payload.get("channels", {}).get("feishu", {})
    if not isinstance(feishu_config, dict):
        return ""

    app_id = normalize_identity_value(feishu_config.get("appId"))
    allow_from = feishu_config.get("allowFrom")
    if not isinstance(allow_from, list):
        return ""

    open_id = ""
    for candidate in allow_from:
        open_id = normalize_identity_value(candidate)
        if open_id:
            break

    if not app_id or not open_id:
        return ""
    return f"feishu-owner:{app_id}:{open_id}"


def resolve_identity_value():
    identity_value = normalize_identity_value(os.getenv(PRIMARY_IDENTITY_ENV, ""))
    if identity_value:
        return identity_value

    identity_value = identity_value_from_cloud_config(DEFAULT_AGENT_CONFIG_PATH)
    if identity_value:
        return identity_value

    state_dir = get_state_dir()
    identity_value = identity_value_from_device_file(state_dir / "identity" / "device.json")
    if identity_value:
        return identity_value

    identity_value = identity_value_from_device_file(DEFAULT_AGENT_IDENTITY_PATH)
    if identity_value:
        return identity_value

    raise RuntimeError(
        "无法自动获取 OpenClaw 标识，请配置 OPENCLAW_IDENTITY，"
        "或检查 /home/gem/workspace/agent/openclaw.json、"
        "~/.openclaw/identity/device.json 与 /home/gem/workspace/agent/identity/device.json"
    )


def resolve_base_url():
    raw_base_url = os.getenv("SAAS_API_URL", "")
    base_url = (raw_base_url or DEFAULT_SAAS_API_URL).strip().rstrip("/")
    if base_url:
        return base_url
    raise RuntimeError("SAAS_API_URL 未配置，且默认 SaaS API 地址为空")


def print_structured_error(exc, api_path=None):
    raw_message = str(exc).strip()
    if raw_message.startswith("{") and raw_message.endswith("}"):
        print(raw_message)
        return 1

    print(
        json.dumps(
            build_error_result(
                "REPORT_PROXY_ERROR",
                raw_message or exc.__class__.__name__,
                api_path=api_path,
            ),
            ensure_ascii=False,
        )
    )
    return 1


def main():
    parser = argparse.ArgumentParser(description="通过 OpenClaw bridge 调用 agent 报表接口")
    parser.add_argument("path", help="业务路径，例如 /agent/order/overview")
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
        help="查询参数 JSON 字符串",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="请求超时时间，单位秒，默认 10",
    )
    args = parser.parse_args()

    try:
        canonical_path = validate_supported_path(args.path, normalize_path=normalize_api_path)
        payload = parse_json_arg(args.payload, "payload")
        query = parse_json_arg(args.query, "query")
        normalized_payload = normalize_payload(canonical_path, payload)

        base_url = resolve_base_url()
        identity_value = resolve_identity_value()
        url = build_bridge_url(base_url)
        bridge_payload = build_bridge_payload(args.method, normalized_payload, query, canonical_path, identity_value)

        response = requests.post(
            url=url,
            headers={
                "Content-Type": "application/json",
                IDENTITY_HEADER: identity_value,
            },
            timeout=args.timeout,
            json=bridge_payload,
        )
        response.raise_for_status()

        try:
            result = extract_business_result(response.json())
        except ValueError:
            print(response.text)
            return 0

        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, RuntimeError, requests.RequestException) as exc:
        return print_structured_error(exc, api_path=args.path)


if __name__ == "__main__":
    sys.exit(main())
