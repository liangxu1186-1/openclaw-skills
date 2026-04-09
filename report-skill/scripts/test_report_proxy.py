import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_proxy import (
    BRIDGE_PROXY_PATH,
    build_bridge_payload,
    build_bridge_url,
    build_error_result,
    extract_business_result,
    normalize_payload,
    print_structured_error,
    resolve_base_url,
    resolve_public_key,
    validate_supported_path,
)


class ReportAgentProxyTest(unittest.TestCase):

    def write_json_file(self, root, relative_path, payload):
        target = Path(root) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_resolve_public_key_prefers_env_over_paired_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "devices/paired.json",
                {"device-1": {"clientId": "cli", "publicKey": "paired-public-key"}},
            )
            with patch.dict(
                os.environ,
                {"OPENCLAW_PUBLIC_KEY": "env-public-key", "OPENCLAW_STATE_DIR": tmpdir},
                clear=False,
            ):
                self.assertEqual("env-public-key", resolve_public_key())

    def test_resolve_public_key_falls_back_to_paired_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "devices/paired.json",
                {"device-1": {"clientId": "cli", "publicKey": "paired-public-key"}},
            )
            with patch.dict(
                os.environ,
                {"OPENCLAW_PUBLIC_KEY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=False,
            ):
                self.assertEqual("paired-public-key", resolve_public_key())

    def test_resolve_public_key_does_not_use_identity_device_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_file(
                tmpdir,
                "identity/device.json",
                {"publicKeyPem": "-----BEGIN PUBLIC KEY-----\nZmFrZQ==\n-----END PUBLIC KEY-----"},
            )
            with patch.dict(
                os.environ,
                {"OPENCLAW_PUBLIC_KEY": "", "OPENCLAW_STATE_DIR": tmpdir},
                clear=False,
            ):
                with self.assertRaises(RuntimeError) as context:
                    resolve_public_key()

            self.assertIn("OPENCLAW_PUBLIC_KEY", str(context.exception))
            self.assertIn("paired.json", str(context.exception))

    def test_resolve_base_url_falls_back_to_default_test_host(self):
        with patch.dict("os.environ", {"SAAS_API_URL": ""}, clear=False):
            self.assertEqual("https://test-shop-kaci.shouqianba.com", resolve_base_url())

    def test_build_bridge_url_uses_fixed_bridge_path(self):
        self.assertEqual(
            "http://localhost:8087" + BRIDGE_PROXY_PATH,
            build_bridge_url("http://localhost:8087/"),
        )

    def test_validate_supported_path_accepts_agent_route(self):
        self.assertEqual("/agent/order/overview", validate_supported_path("/agent/order/overview"))

    def test_validate_supported_path_accepts_defined_routes_from_each_domain(self):
        self.assertEqual("/agent/order/business-type", validate_supported_path("/agent/order/business-type"))
        self.assertEqual("/agent/goods/overview", validate_supported_path("/agent/goods/overview"))
        self.assertEqual("/agent/goods/income-subject", validate_supported_path("/agent/goods/income-subject"))
        self.assertEqual("/agent/payment/compose", validate_supported_path("/agent/payment/compose"))
        self.assertEqual("/agent/marketing/promotion-summary", validate_supported_path("/agent/marketing/promotion-summary"))
        self.assertEqual("/agent/member/preference", validate_supported_path("/agent/member/preference"))

    def test_validate_supported_path_rejects_removed_member_ranking_route(self):
        with self.assertRaises(ValueError) as context:
            validate_supported_path("/agent/member/ranking")

        self.assertIn("/agent/member/ranking", str(context.exception))

    def test_validate_supported_path_rejects_removed_goods_focus_route(self):
        with self.assertRaises(ValueError) as context:
            validate_supported_path("/agent/goods/focus")

        self.assertIn("/agent/goods/focus", str(context.exception))

    def test_validate_supported_path_rejects_removed_payment_split_routes(self):
        with self.assertRaises(ValueError) as context:
            validate_supported_path("/agent/payment/subject-compose")

        self.assertIn("/agent/payment/subject-compose", str(context.exception))

    def test_validate_supported_path_rejects_unknown_route_with_candidates(self):
        with self.assertRaises(ValueError) as context:
            validate_supported_path("/agent/order/ranking")

        message = str(context.exception)
        self.assertIn("/agent/order/ranking", message)
        self.assertIn("/agent/order/shop-ranking", message)
        self.assertIn("./api/agent.md", message)

    def test_agent_route_payload_uses_unified_time_fields(self):
        payload = normalize_payload(
            "/agent/order/shop-ranking",
            {"startTime": 20260301, "endTime": 20260331, "flag": 2},
        )

        self.assertEqual(20260301, payload["startTime"])
        self.assertEqual(20260331, payload["endTime"])
        self.assertEqual(2, payload["flag"])

    def test_agent_route_payload_defaults_flag_to_business_day(self):
        payload = normalize_payload(
            "/agent/order/overview",
            {"startTime": 20260301, "endTime": 20260331},
        )

        self.assertEqual(2, payload["flag"])

    def test_new_defined_route_payload_defaults_flag_to_business_day(self):
        payload = normalize_payload(
            "/agent/payment/discount-overview",
            {"startTime": 20260301, "endTime": 20260331},
        )

        self.assertEqual(2, payload["flag"])

    def test_agent_route_payload_rejects_legacy_time_fields(self):
        with self.assertRaises(ValueError) as context:
            normalize_payload(
                "/agent/order/shop-ranking",
                {"dateType": 2, "startDate": 20260301, "endDate": 20260331, "flag": 2},
            )

        error = json.loads(str(context.exception))
        self.assertEqual("PAYLOAD_VALIDATION_ERROR", error["code"])
        self.assertEqual("/agent/order/shop-ranking", error["path"])
        self.assertEqual(["dateType", "endDate", "startDate"], error["detail"]["forbiddenFields"])

    def test_defined_goods_route_rejects_legacy_fields(self):
        with self.assertRaises(ValueError) as context:
            normalize_payload(
                "/agent/goods/refund-ranking",
                {"startTime": 20260301, "endTime": 20260331, "flag": 2, "metricsType": 10},
            )

        error = json.loads(str(context.exception))
        self.assertEqual("/agent/goods/refund-ranking", error["path"])
        self.assertEqual(["metricsType"], error["detail"]["forbiddenFields"])

    def test_agent_route_requires_start_end_and_flag(self):
        with self.assertRaises(ValueError) as context:
            normalize_payload("/agent/member/preference", {})

        error = json.loads(str(context.exception))
        self.assertEqual(["endTime", "startTime"], error["detail"]["missingFields"])

    def test_agent_route_rejects_date_range_longer_than_90_days(self):
        with self.assertRaises(ValueError) as context:
            normalize_payload(
                "/agent/order/overview",
                {"startTime": 20260101, "endTime": 20260705, "flag": 2},
            )

        error = json.loads(str(context.exception))
        self.assertEqual("PAYLOAD_VALIDATION_ERROR", error["code"])
        self.assertEqual("/agent/order/overview", error["path"])
        self.assertEqual(90, error["detail"]["maxRangeDays"])

    def test_build_bridge_payload_accepts_agent_route(self):
        payload = normalize_payload(
            "/agent/member/preference",
            {"startTime": 20260301, "endTime": 20260331, "flag": 2},
        )
        bridge_payload = build_bridge_payload("POST", payload, None, "/agent/member/preference", "public-key-demo")

        self.assertEqual("/agent/member/preference", bridge_payload["targetPath"])
        self.assertEqual('{"startTime":20260301,"endTime":20260331,"flag":2}'.replace(" ", ""), bridge_payload["payload"])

    def test_build_bridge_payload_accepts_marketing_route(self):
        payload = normalize_payload(
            "/agent/marketing/activity-summary",
            {"startTime": 20260301, "endTime": 20260331, "flag": 2},
        )
        bridge_payload = build_bridge_payload("POST", payload, None, "/agent/marketing/activity-summary", "public-key-demo")

        self.assertEqual("/agent/marketing/activity-summary", bridge_payload["targetPath"])

    def test_extract_business_result_unwraps_bridge_success_payload(self):
        response_json = {
            "success": True,
            "code": 0,
            "message": "success",
            "data": {"orderAmount": 1},
        }
        self.assertEqual({"orderAmount": 1}, extract_business_result(response_json))

    def test_extract_business_result_keeps_error_body(self):
        response_json = {
            "success": False,
            "code": "PARAM_INVALID",
            "message": "startTime/endTime 不能为空",
        }
        self.assertEqual(response_json, extract_business_result(response_json))

    def test_build_error_result_keeps_structured_fields(self):
        result = build_error_result(
            "PAYLOAD_VALIDATION_ERROR",
            "门店榜单只传 startTime/endTime/flag。",
            error_type="payload_validation",
            api_path="/agent/order/shop-ranking",
            detail={"missingFields": ["startTime"]},
        )

        self.assertFalse(result["success"])
        self.assertEqual("payload_validation", result["errorType"])
        self.assertEqual("/agent/order/shop-ranking", result["path"])
        self.assertEqual(["startTime"], result["detail"]["missingFields"])

    def test_print_structured_error_passes_through_json_payload(self):
        with patch("builtins.print") as mock_print:
            exit_code = print_structured_error(ValueError('{"success":false,"code":"PAYLOAD_VALIDATION_ERROR"}'))

        self.assertEqual(1, exit_code)
        mock_print.assert_called_once_with('{"success":false,"code":"PAYLOAD_VALIDATION_ERROR"}')


if __name__ == "__main__":
    unittest.main()
