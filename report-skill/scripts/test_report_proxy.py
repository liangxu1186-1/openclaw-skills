import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_proxy import (
    BRIDGE_PROXY_PATH,
    build_bridge_payload,
    build_bridge_url,
    extract_business_result,
)


class ReportProxyTest(unittest.TestCase):

    def test_build_bridge_url_uses_fixed_bridge_path(self):
        self.assertEqual(
            "http://localhost:8087" + BRIDGE_PROXY_PATH,
            build_bridge_url("http://localhost:8087/"),
        )

    def test_build_bridge_payload_wraps_target_path_and_business_json(self):
        payload = build_bridge_payload(
            "POST",
            {"flag": 2, "startDate": 20250601},
            {"traceId": "demo"},
            "report/goodsPosCateSaleSummary",
            "public-key-demo",
        )
        self.assertEqual("/report/goodsPosCateSaleSummary", payload["targetPath"])
        self.assertEqual("public-key-demo", payload["publicKey"])
        self.assertEqual("POST", payload["method"])
        self.assertEqual('{"flag":2,"startDate":20250601}', payload["payload"])
        self.assertEqual('{"traceId":"demo"}', payload["query"])

    def test_extract_business_result_unwraps_bridge_success_payload(self):
        response_json = {
            "success": True,
            "code": 0,
            "message": "success",
            "data": {"list": [1, 2, 3]},
        }
        self.assertEqual({"list": [1, 2, 3]}, extract_business_result(response_json))

    def test_extract_business_result_keeps_error_body(self):
        response_json = {
            "success": False,
            "code": 400,
            "message": "payload 不是合法 JSON",
        }
        self.assertEqual(response_json, extract_business_result(response_json))


if __name__ == "__main__":
    unittest.main()
