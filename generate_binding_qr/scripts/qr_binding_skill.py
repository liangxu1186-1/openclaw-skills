#!/usr/bin/env python3
import argparse
import base64
import importlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
import warnings

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

QR_DURATION_SECONDS = 300
QR_DURATION_LABEL = "5分钟"
DEFAULT_TIMEOUT = 10
DEFAULT_STATE_DIR = "~/.openclaw"
DEFAULT_AGENT_IDENTITY_PATH = Path("/home/gem/workspace/agent/identity/device.json")
DEFAULT_SAAS_API_URL = "https://test-shop-kaci.shouqianba.com"
QR_IMAGE_PATH = "/report/openclaw/binding/qr-image"
PRIMARY_IDENTITY_ENV = "OPENCLAW_IDENTITY"
IDENTITY_REQUEST_FIELD = "publicKey"


def ensure_python_dependencies() -> None:
    try:
        importlib.import_module("requests")
        return
    except ModuleNotFoundError:
        pass

    skill_dir = Path(__file__).resolve().parent.parent
    requirements_path = skill_dir / "requirements.txt"
    install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--user",
        "--default-timeout",
        "120",
        "--retries",
        "5",
    ]
    if requirements_path.exists():
        install_cmd.extend(["-r", str(requirements_path)])
    else:
        install_cmd.extend(["requests>=2.31.0"])

    try:
        subprocess.check_call(install_cmd)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "自动安装 requests 依赖失败，请检查宿主机网络是否能访问 files.pythonhosted.org，"
            "或预先执行: python3 -m pip install --user -r requirements.txt"
        ) from exc


ensure_python_dependencies()
requests = importlib.import_module("requests")


def summarize_response_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    compact = " ".join(str(text).split())
    if len(compact) <= 200:
        return compact
    return compact[:200] + "..."


def get_state_dir() -> Path:
    return Path(os.getenv("OPENCLAW_STATE_DIR", DEFAULT_STATE_DIR)).expanduser()


def load_json_file(path: Path) -> Optional[object]:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_identity_value(value: object) -> Optional[str]:
    if value is None or isinstance(value, (dict, list, tuple, set, bool)):
        return None
    normalized = str(value).strip()
    return normalized or None


def resolve_identity_value_from_device_file(identity_path: Path) -> Optional[str]:
    payload = load_json_file(identity_path)
    if not isinstance(payload, dict):
        return None

    return normalize_identity_value(payload.get("deviceId"))


def resolve_identity_value(explicit_identity: Optional[str]) -> Optional[str]:
    normalized_explicit_identity = normalize_identity_value(explicit_identity)
    if normalized_explicit_identity:
        return normalized_explicit_identity

    env_identity = normalize_identity_value(os.getenv(PRIMARY_IDENTITY_ENV))
    if env_identity:
        return env_identity

    identity_value = resolve_identity_value_from_device_file(get_state_dir() / "identity" / "device.json")
    if identity_value:
        return identity_value

    return resolve_identity_value_from_device_file(DEFAULT_AGENT_IDENTITY_PATH)


def resolve_base_url() -> str:
    raw_base_url = os.getenv("SAAS_API_URL", "")
    base_url = (raw_base_url or DEFAULT_SAAS_API_URL).strip().rstrip("/")
    if base_url:
        return base_url
    raise RuntimeError("SAAS_API_URL 未配置，且默认 SaaS API 地址为空")


def build_qr_image_url(base_url: str) -> str:
    return base_url.rstrip("/") + QR_IMAGE_PATH


def extract_image_url(response_json: object) -> str:
    if isinstance(response_json, dict) and "imageUrl" in response_json:
        image_url = str(response_json.get("imageUrl", "")).strip()
        if image_url:
            return image_url

    if isinstance(response_json, dict) and response_json.get("success") and isinstance(response_json.get("data"), dict):
        image_url = str(response_json["data"].get("imageUrl", "")).strip()
        if image_url:
            return image_url

    raise RuntimeError("二维码图片接口未返回 imageUrl")


def fetch_remote_qr_image_url(identity_value: Optional[str]) -> str:
    resolved_identity = resolve_identity_value(identity_value)
    if not resolved_identity:
        raise RuntimeError(
            "错误：未能在系统中找到 OpenClaw 标识，请手动提供或检查 OPENCLAW_IDENTITY、"
            "identity/device.json，或固定路径 /home/gem/workspace/agent/identity/device.json。"
        )

    endpoint = build_qr_image_url(resolve_base_url())
    try:
        response = requests.post(
            endpoint,
            json={IDENTITY_REQUEST_FIELD: resolved_identity},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        response_text = summarize_response_text(getattr(response, "text", ""))
        details = [f"请求二维码图片接口失败: {endpoint}"]
        if status_code is not None:
            details.append(f"状态码: {status_code}")
        if response_text:
            details.append(f"响应: {response_text}")
        else:
            details.append(f"原因: {exc}")
        raise RuntimeError(", ".join(details)) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"请求二维码图片接口失败: {endpoint}, 原因: {exc}") from exc

    try:
        response_json = response.json()
    except ValueError as exc:
        raise RuntimeError(f"二维码图片接口返回的不是合法 JSON: {endpoint}") from exc

    return extract_image_url(response_json)


def download_remote_qr_image_bytes(image_url: str) -> bytes:
    try:
        response = requests.get(image_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        response_text = summarize_response_text(getattr(response, "text", ""))
        details = [f"下载二维码图片失败: {image_url}"]
        if status_code is not None:
            details.append(f"状态码: {status_code}")
        if response_text:
            details.append(f"响应: {response_text}")
        else:
            details.append(f"原因: {exc}")
        raise RuntimeError(", ".join(details)) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"下载二维码图片失败: {image_url}, 原因: {exc}") from exc

    image_bytes = response.content
    if not image_bytes:
        raise RuntimeError(f"下载二维码图片失败: {image_url}, 原因: 响应体为空")

    return image_bytes


def encode_png_bytes_as_data_uri(image_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")


def render_markdown_result(media_path: str) -> str:
    return f"请在{QR_DURATION_LABEL}内使用云助手小程序扫码绑定\n![扫码绑定]({media_path})"


def write_output(content: str) -> None:
    sys.stdout.write(content)


def run_healthcheck(trace: bool):
    timings = {}

    t = time.perf_counter()
    identity_value = resolve_identity_value(None)
    timings["identity"] = int((time.perf_counter() - t) * 1000)

    t = time.perf_counter()
    try:
        base_url = resolve_base_url()
        base_url_ok = True
        message = None
    except Exception as exc:
        base_url = None
        base_url_ok = False
        message = str(exc)
    timings["baseUrl"] = int((time.perf_counter() - t) * 1000)

    return {
        "ok": bool(identity_value) and base_url_ok,
        "stage": "healthcheck",
        "identityLoaded": bool(identity_value),
        "baseUrlLoaded": base_url_ok,
        "qrReady": bool(identity_value) and base_url_ok,
        "timings": timings if trace else None,
        "message": message,
    }


def run_warmup(trace: bool):
    timings = {}

    t = time.perf_counter()
    identity_value = resolve_identity_value(None)
    timings["identity"] = int((time.perf_counter() - t) * 1000)

    t = time.perf_counter()
    base_url = resolve_base_url()
    endpoint = build_qr_image_url(base_url)
    timings["endpoint"] = int((time.perf_counter() - t) * 1000)

    return {
        "ok": bool(identity_value) and bool(endpoint),
        "stage": "warmup",
        "identityLoaded": bool(identity_value),
        "endpoint": endpoint,
        "timings": timings if trace else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OpenClaw binding QR code.")
    parser.add_argument("--identity", help="Explicit OpenClaw identity value", default=None)
    parser.add_argument(
        "--format",
        choices=["image-url", "markdown"],
        default="image-url",
        help="Output remote image URL or Markdown with the remote image URL.",
    )
    parser.add_argument("--healthcheck", action="store_true", help="检查依赖与标识可用性")
    parser.add_argument("--warmup", action="store_true", help="执行预热，检查标识和二维码接口地址")
    parser.add_argument("--trace", action="store_true", help="输出分段耗时信息")
    args = parser.parse_args()

    if args.healthcheck:
        write_output(json.dumps({k: v for k, v in run_healthcheck(args.trace).items() if v is not None}, ensure_ascii=False))
        return

    if args.warmup:
        write_output(json.dumps({k: v for k, v in run_warmup(args.trace).items() if v is not None}, ensure_ascii=False))
        return

    if args.format == "markdown":
        image_url = fetch_remote_qr_image_url(args.identity)
        image_bytes = download_remote_qr_image_bytes(image_url)
        write_output(render_markdown_result(encode_png_bytes_as_data_uri(image_bytes)))
        return

    write_output(fetch_remote_qr_image_url(args.identity))


if __name__ == "__main__":
    main()
