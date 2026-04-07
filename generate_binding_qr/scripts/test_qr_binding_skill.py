import unittest
from unittest.mock import Mock, patch
import base64
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr_binding_skill


class QrBindingSkillTest(unittest.TestCase):

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
    @patch("qr_binding_skill.resolve_public_key", return_value="pk-test")
    @patch("qr_binding_skill.requests.post")
    def test_fetch_remote_qr_image_url_reads_service_response(self, mock_post: Mock, _mock_public_key: Mock, _mock_base_url: Mock):
        response = Mock()
        response.json.return_value = {"imageUrl": "https://oss.example.com/openclaw/demo.png", "expireAt": 1}
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        result = qr_binding_skill.fetch_remote_qr_image_url(None)

        self.assertEqual("https://oss.example.com/openclaw/demo.png", result)
        mock_post.assert_called_once_with(
            "http://127.0.0.1:8087/report/openclaw/binding/qr-image",
            json={"publicKey": "pk-test"},
            timeout=qr_binding_skill.DEFAULT_TIMEOUT,
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_public_key", return_value="pk-test")
    @patch("qr_binding_skill.requests.post", side_effect=requests.exceptions.ConnectionError("dial tcp 127.0.0.1:8087: connect: connection refused"))
    def test_fetch_remote_qr_image_url_reports_endpoint_and_cause(self, _mock_post: Mock, _mock_public_key: Mock, _mock_base_url: Mock):
        with self.assertRaises(RuntimeError) as context:
            qr_binding_skill.fetch_remote_qr_image_url(None)

        self.assertEqual(
            "请求二维码图片接口失败: http://127.0.0.1:8087/report/openclaw/binding/qr-image, 原因: dial tcp 127.0.0.1:8087: connect: connection refused",
            str(context.exception),
        )

    @patch("qr_binding_skill.resolve_base_url", return_value="http://127.0.0.1:8087")
    @patch("qr_binding_skill.resolve_public_key", return_value="pk-test")
    @patch("qr_binding_skill.requests.post")
    def test_fetch_remote_qr_image_url_reports_response_body_when_status_invalid(self, mock_post: Mock, _mock_public_key: Mock, _mock_base_url: Mock):
        response = Mock()
        response.status_code = 500
        response.text = "{\"message\":\"publicKey不能为空\"}"
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error", response=response)
        mock_post.return_value = response

        with self.assertRaises(RuntimeError) as context:
            qr_binding_skill.fetch_remote_qr_image_url(None)

        self.assertEqual(
            "请求二维码图片接口失败: http://127.0.0.1:8087/report/openclaw/binding/qr-image, 状态码: 500, 响应: {\"message\":\"publicKey不能为空\"}",
            str(context.exception),
        )

    def test_render_markdown_result_uses_short_image_url(self):
        markdown = qr_binding_skill.render_markdown_result("https://oss.example.com/openclaw/demo.png")

        self.assertIn("请在5分钟内使用云助手小程序扫码绑定", markdown)
        self.assertIn(
            "![扫码绑定](https://oss.example.com/openclaw/demo.png)",
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
            "请在5分钟内使用云助手小程序扫码绑定\n"
            f"![扫码绑定](data:image/png;base64,{expected_base64})",
            rendered_markdown,
        )
        mock_get.assert_called_once_with(
            "https://oss.example.com/openclaw/demo.png",
            timeout=qr_binding_skill.DEFAULT_TIMEOUT,
        )


if __name__ == "__main__":
    unittest.main()
