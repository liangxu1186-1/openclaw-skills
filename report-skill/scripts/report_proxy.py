import argparse
import base64
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
PUBLIC_KEY_HEADER = "X-OpenClaw-PublicKey"
TARGET_PATH_PARAM = "targetPath"
PUBLIC_KEY_FIELD = "publicKey"
PAYLOAD_FIELD = "payload"
QUERY_FIELD = "query"
METHOD_FIELD = "method"
DEFAULT_TIMEOUT = 10
DEFAULT_STATE_DIR = "~/.openclaw"
DEFAULT_SAAS_API_URL = "https://test-shop-kaci.shouqianba.com"
DEFAULT_FLAG = 2
MAX_RANGE_DAYS = 183


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


def build_bridge_payload(method, payload, query, api_path, public_key):
    return {
        TARGET_PATH_PARAM: validate_supported_path(api_path, normalize_path=normalize_api_path),
        PUBLIC_KEY_FIELD: public_key,
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
        public_key = resolve_public_key()
        url = build_bridge_url(base_url)
        bridge_payload = build_bridge_payload(args.method, normalized_payload, query, canonical_path, public_key)

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
            return 0

        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, RuntimeError, requests.RequestException) as exc:
        return print_structured_error(exc, api_path=args.path)


if __name__ == "__main__":
    sys.exit(main())
