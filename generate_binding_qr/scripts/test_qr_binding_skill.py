import base64
import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import Mock, patch
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr_binding_skill


class QrBindingSkillTest(unittest.TestCase):

    fixed_fallback_identity_path = Path("/home/gem/workspace/agent/identity/device.json")
    fixed_cloud_config_path = Path("/home/gem/workspace/agent/openclaw.json")

    def write_json_file(self, root, relative_path, payload):
        target = Path(root) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_resolve_identity_value_prefers_env_over_identity_device_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "identity/device.json",
                {"deviceId": "device-id-from-file"},
            )

            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "env-public-key", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.home", return_value=Path(tmpdir)):
                self.assertEqual("env-public-key", qr_binding_skill.resolve_identity_value(None))

    def test_resolve_identity_value_falls_back_to_identity_device_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "identity/device.json",
                {"deviceId": "device-id-from-file"},
            )

            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.home", return_value=Path(tmpdir)):
                self.assertEqual("device-id-from-file", qr_binding_skill.resolve_identity_value(None))

    def test_resolve_identity_value_does_not_use_paired_devices_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "devices/paired.json",
                {"device-1": {"clientId": "cli", "publicKey": "paired-public-key"}},
            )

            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.home", return_value=Path(tmpdir)):
                self.assertIsNone(qr_binding_skill.resolve_identity_value(None))

    def test_resolve_identity_value_does_not_use_pem_file_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / ".identity" / "pub.key"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "-----BEGIN PUBLIC KEY-----\nZmFrZQ==\n-----END PUBLIC KEY-----\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.cwd", return_value=Path(tmpdir)), patch(
                "qr_binding_skill.Path.home", return_value=Path(tmpdir)
            ):
                self.assertIsNone(qr_binding_skill.resolve_identity_value(None))

    def test_resolve_identity_value_falls_back_to_fixed_agent_identity_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.home", return_value=Path(tmpdir)), patch(
                "qr_binding_skill.load_json_file",
                side_effect=lambda path: {"deviceId": "device-id-from-fixed-fallback"}
                if path == self.fixed_fallback_identity_path
                else None,
            ):
                self.assertEqual("device-id-from-fixed-fallback", qr_binding_skill.resolve_identity_value(None))

    def test_resolve_identity_value_falls_back_to_feishu_owner_identity_from_cloud_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(
                os.environ,
                {"OPENCLAW_IDENTITY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=True,
            ), patch("qr_binding_skill.Path.home", return_value=Path(tmpdir)), patch(
                "qr_binding_skill.load_json_file",
                side_effect=lambda path: {
                    "channels": {
                        "feishu": {
                            "appId": "cli_a95d229d78785cbc",
                            "allowFrom": ["ou_e012616c60661b6460fb9bf4bd4d9b5d"],
                        }
                    }
                }
                if path == self.fixed_cloud_config_path
                else None,
            ):
                self.assertEqual(
                    "feishu-owner:cli_a95d229d78785cbc:ou_e012616c60661b6460fb9bf4bd4d9b5d",
                    qr_binding_skill.resolve_identity_value(None),
                )

    def test_extract_image_url_supports_direct_response(self):
        self.assertEqual(
            "https://oss.example.com/demo.png",
            qr_binding_skill.extract_image_url({"imageUrl": "https://oss.example.com/demo.png", "expireAt": 1}),
        )

    def test_extract_image_url_supports_wrapped_response(self):
        self.assertEqual(
            "https://oss.example.com/demo.png",
            qr_binding_skill.extract_image_url(
                {"success": True, "data": {"imageUrl": "https://oss.example.com/demo.png", "expireAt": 1}}
            ),
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_identity_value", return_value="id-test")
    @patch("qr_binding_skill.requests.post")
    def test_fetch_remote_qr_image_url_reads_service_response(self, mock_post: Mock, _mock_identity: Mock, _mock_base_url: Mock):
        response = Mock()
        response.json.return_value = {"imageUrl": "https://oss.example.com/openclaw/demo.png", "expireAt": 1}
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        result = qr_binding_skill.fetch_remote_qr_image_url(None, 1)

        self.assertEqual("https://oss.example.com/openclaw/demo.png", result)
        mock_post.assert_called_once_with(
            "http://127.0.0.1:8087/report/openclaw/binding/qr-image",
            json={"publicKey": "id-test", "bindType": 1},
            timeout=qr_binding_skill.DEFAULT_TIMEOUT,
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_identity_value", return_value="id-test")
    @patch("qr_binding_skill.requests.post")
    def test_fetch_remote_qr_image_url_sends_unbind_type(self, mock_post: Mock, _mock_identity: Mock, _mock_base_url: Mock):
        response = Mock()
        response.json.return_value = {"imageUrl": "https://oss.example.com/openclaw/demo.png", "expireAt": 1}
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        qr_binding_skill.fetch_remote_qr_image_url(None, 0)

        mock_post.assert_called_once_with(
            "http://127.0.0.1:8087/report/openclaw/binding/qr-image",
            json={"publicKey": "id-test", "bindType": 0},
            timeout=qr_binding_skill.DEFAULT_TIMEOUT,
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_identity_value", return_value="id-test")
    @patch("qr_binding_skill.requests.post", side_effect=requests.exceptions.ConnectionError("dial tcp 127.0.0.1:8087: connect: connection refused"))
    def test_fetch_remote_qr_image_url_reports_endpoint_and_cause(self, _mock_post: Mock, _mock_identity: Mock, _mock_base_url: Mock):
        with self.assertRaises(RuntimeError) as context:
            qr_binding_skill.fetch_remote_qr_image_url(None, 1)

        self.assertEqual(
            "请求二维码图片接口失败: http://127.0.0.1:8087/report/openclaw/binding/qr-image, 原因: dial tcp 127.0.0.1:8087: connect: connection refused",
            str(context.exception),
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_identity_value", return_value="id-test")
    @patch("qr_binding_skill.requests.post")
    def test_fetch_remote_qr_image_url_reports_response_body_when_status_invalid(self, mock_post: Mock, _mock_identity: Mock, _mock_base_url: Mock):
        response = Mock()
        response.status_code = 500
        response.text = "{\"message\":\"openClawId不能为空\"}"
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error", response=response)
        mock_post.return_value = response

        with self.assertRaises(RuntimeError) as context:
            qr_binding_skill.fetch_remote_qr_image_url(None, 1)

        self.assertEqual(
            "请求二维码图片接口失败: http://127.0.0.1:8087/report/openclaw/binding/qr-image, 状态码: 500, 响应: {\"message\":\"openClawId不能为空\"}",
            str(context.exception),
        )

    def test_render_markdown_result_uses_short_image_url(self):
        markdown = qr_binding_skill.render_markdown_result("https://oss.example.com/openclaw/demo.png", 1)

        self.assertIn("请在10分钟内使用云助手小程序扫码绑定", markdown)
        self.assertIn(
            "![扫码绑定](https://oss.example.com/openclaw/demo.png)",
            markdown,
        )

    def test_render_markdown_result_uses_unbind_copy(self):
        markdown = qr_binding_skill.render_markdown_result("https://oss.example.com/openclaw/demo.png", 0)

        self.assertIn("请在10分钟内使用云助手小程序扫码解绑", markdown)
        self.assertIn(
            "![扫码解绑](https://oss.example.com/openclaw/demo.png)",
            markdown,
        )

    @patch("qr_binding_skill.fetch_remote_qr_image_url", return_value="https://oss.example.com/openclaw/demo.png")
    @patch("qr_binding_skill.requests.get")
    def test_main_markdown_outputs_base64_image_data_uri(self, mock_get: Mock, _mock_fetch_remote_url: Mock):
        image_bytes = b"png-binary"
        response = Mock()
        response.content = image_bytes
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with patch.object(sys, "argv", ["qr_binding_skill.py", "--format", "markdown"]), patch(
            "qr_binding_skill.write_output"
        ) as mock_write_output:
            qr_binding_skill.main()

        rendered_markdown = mock_write_output.call_args.args[0]
        expected_base64 = base64.b64encode(image_bytes).decode("ascii")
        self.assertEqual(
            "请在10分钟内使用云助手小程序扫码绑定\n"
            f"![扫码绑定](data:image/png;base64,{expected_base64})",
            rendered_markdown,
        )
        mock_get.assert_called_once_with(
            "https://oss.example.com/openclaw/demo.png",
            timeout=qr_binding_skill.DEFAULT_TIMEOUT,
        )

    @patch("qr_binding_skill.fetch_remote_qr_image_url", return_value="https://oss.example.com/openclaw/demo.png")
    @patch("qr_binding_skill.requests.get")
    def test_main_markdown_outputs_unbind_image_data_uri(self, mock_get: Mock, _mock_fetch_remote_url: Mock):
        image_bytes = b"png-binary"
        response = Mock()
        response.content = image_bytes
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with patch.object(sys, "argv", ["qr_binding_skill.py", "--format", "markdown", "--bind-type", "0"]), patch(
            "qr_binding_skill.write_output"
        ) as mock_write_output:
            qr_binding_skill.main()

        rendered_markdown = mock_write_output.call_args.args[0]
        expected_base64 = base64.b64encode(image_bytes).decode("ascii")
        self.assertEqual(
            "请在10分钟内使用云助手小程序扫码解绑\n"
            f"![扫码解绑](data:image/png;base64,{expected_base64})",
            rendered_markdown,
        )


if __name__ == "__main__":
    unittest.main()
