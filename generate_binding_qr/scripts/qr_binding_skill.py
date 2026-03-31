#!/usr/bin/env python3
import argparse
import base64
from datetime import datetime
import importlib
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Union

QR_DURATION_SECONDS = 300
QR_DURATION_LABEL = "5分钟"


def ensure_python_dependencies() -> None:
    try:
        importlib.import_module("qrcode")
        importlib.import_module("qrcode.image.pure")
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
        "--prefer-binary",
    ]
    if requirements_path.exists():
        install_cmd.extend(["-r", str(requirements_path)])
    else:
        install_cmd.extend(["qrcode[png]>=7.4.2"])

    try:
        subprocess.check_call(install_cmd)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "自动安装二维码依赖失败，请检查宿主机网络是否能访问 files.pythonhosted.org，"
            "或预先执行: python3 -m pip install --user -r requirements.txt"
        ) from exc


ensure_python_dependencies()
qrcode = importlib.import_module("qrcode")
PyPNGImage = importlib.import_module("qrcode.image.pure").PyPNGImage
QR_ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_Q
QR_BOX_SIZE = 2
QR_BORDER = 4


def resolve_public_key_from_paired_devices() -> Optional[str]:
    paired_path = Path.home() / ".openclaw" / "devices" / "paired.json"
    if not paired_path.exists():
        return None

    try:
        payload = json.loads(paired_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    entries = [value for value in payload.values() if isinstance(value, dict)]
    preferred_entries = []
    fallback_entries = []

    for entry in entries:
        public_key = entry.get("publicKey")
        if not isinstance(public_key, str) or not public_key.strip():
            continue

        client_id = entry.get("clientId")
        platform = entry.get("platform")
        if client_id == "cli" and platform == "darwin":
            preferred_entries.append(entry)
        else:
            fallback_entries.append(entry)

    for entry in preferred_entries + fallback_entries:
        public_key = entry.get("publicKey")
        if isinstance(public_key, str) and public_key.strip():
            return public_key.strip()

    return None


def resolve_public_key(explicit_key: Optional[str]) -> Optional[str]:
    if explicit_key:
        return explicit_key

    env_key = os.getenv("OPENCLAW_PUBKEY")
    if env_key:
        return env_key

    paired_key = resolve_public_key_from_paired_devices()
    if paired_key:
        return paired_key

    skill_dir = Path(__file__).resolve().parent.parent
    search_roots = [Path.cwd(), skill_dir]
    candidate_relpaths = [
        Path("keys/public.pem"),
        Path("config/id_rsa.pub"),
        Path(".identity/pub.key"),
    ]

    for root in search_roots:
        for relpath in candidate_relpaths:
            candidate = root / relpath
            if candidate.exists():
                return candidate.read_text(encoding="utf-8").strip()

    return None


def build_binding_payload(public_key: str) -> str:
    payload = {
        "scenario": "openclaw-register",
        "params": {
            "key": public_key,
            "createTime": int(datetime.now().strftime("%Y%m%d%H%M%S")),
            "duration": QR_DURATION_SECONDS,
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def generate_binding_qr_png(public_key: Optional[str] = None) -> Union[bytes, str]:
    pk = resolve_public_key(public_key)
    if not pk:
        return "错误：未能在系统中找到公钥，请手动提供或检查密钥配置文件。"

    try:
        payload = build_binding_payload(pk)
        qr = qrcode.QRCode(
            version=1,
            # Keep the inline PNG shorter so the chat renderer is less likely
            # to break the base64 payload, while still retaining a standard quiet zone.
            error_correction=QR_ERROR_CORRECTION,
            box_size=QR_BOX_SIZE,
            border=QR_BORDER,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=PyPNGImage,
            fill_color="black",
            back_color="white",
        )
        buffered = io.BytesIO()
        img.save(buffered)
        return buffered.getvalue()
    except Exception as exc:
        return f"二维码生成失败: {exc}"


def generate_binding_qr(public_key: Optional[str] = None) -> str:
    png_bytes = generate_binding_qr_png(public_key)
    if isinstance(png_bytes, str):
        return png_bytes

    img_base64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"


def render_markdown_result(media_path: str) -> str:
    return f"请在{QR_DURATION_LABEL}内使用云助手小程序扫码绑定\n![扫码绑定]({media_path})"


def write_output(content: str) -> None:
    sys.stdout.write(content)


def run_healthcheck(trace: bool):
    timings = {}
    t0 = time.perf_counter()
    # 依赖检查（模块已导入，这里仅给出 0ms 占位或再次访问）
    t = time.perf_counter()
    try:
        importlib.import_module("qrcode")
        importlib.import_module("qrcode.image.pure")
        deps_ok = True
    except Exception:
        deps_ok = False
    timings["pythonDeps"] = int((time.perf_counter() - t) * 1000)

    t = time.perf_counter()
    pk = resolve_public_key(None)
    timings["publicKey"] = int((time.perf_counter() - t) * 1000)

    return {
        "ok": bool(deps_ok),
        "stage": "healthcheck",
        "pythonDeps": bool(deps_ok),
        "publicKeyLoaded": bool(pk),
        "qrReady": bool(deps_ok),
        "timings": timings if trace else None,
    }


def run_warmup(trace: bool):
    timings = {}
    t = time.perf_counter()
    # 生成一次内存二维码（使用占位 key，避免真实业务）
    try:
        payload = build_binding_payload("WARMUP-KEY")
        qr = qrcode.QRCode(
            version=1,
            error_correction=QR_ERROR_CORRECTION,
            box_size=QR_BOX_SIZE,
            border=QR_BORDER,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(image_factory=PyPNGImage, fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf)
        ok = True
        msg = None
    except Exception as exc:
        ok = False
        msg = str(exc)
    timings["qrBuild"] = int((time.perf_counter() - t) * 1000)

    # 公钥解析（不强制）
    t = time.perf_counter()
    pk = resolve_public_key(None)
    timings["publicKey"] = int((time.perf_counter() - t) * 1000)

    return {
        "ok": ok,
        "stage": "warmup",
        "pythonDeps": True,
        "publicKeyLoaded": bool(pk),
        "timings": timings if trace else None,
        "message": msg,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OpenClaw binding QR code.")
    parser.add_argument("--public-key", help="Explicit public key content", default=None)
    parser.add_argument(
        "--format",
        choices=["data-url", "markdown"],
        default="data-url",
        help="Output raw data URL or Markdown with inline data URL.",
    )
    parser.add_argument("--healthcheck", action="store_true", help="检查依赖与密钥可用性")
    parser.add_argument("--warmup", action="store_true", help="执行预热，在内存生成一次二维码")
    parser.add_argument("--trace", action="store_true", help="输出分段耗时信息")
    args = parser.parse_args()

    if args.healthcheck:
        write_output(json.dumps({k: v for k, v in run_healthcheck(args.trace).items() if v is not None}, ensure_ascii=False))
        return

    if args.warmup:
        write_output(json.dumps({k: v for k, v in run_warmup(args.trace).items() if v is not None}, ensure_ascii=False))
        return

    if args.format == "markdown":
        png_bytes = generate_binding_qr_png(args.public_key)
        if isinstance(png_bytes, str):
            write_output(png_bytes)
            return

        image_data_url = f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"
        write_output(render_markdown_result(image_data_url))
        return

    write_output(generate_binding_qr(args.public_key))


if __name__ == "__main__":
    main()
