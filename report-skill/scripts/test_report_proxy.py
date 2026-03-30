import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_proxy import (
    BRIDGE_PROXY_PATH,
    build_bridge_payload,
    build_bridge_url,
    compact_result,
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

    def test_compact_order_business_daily_keeps_core_metrics_only(self):
        result = {
            "orderAmount": 12888.5,
            "actualReceiptAmount": 12001.2,
            "discountAmount": 887.3,
            "refundAmount": 21.0,
            "saleOrderNum": 318,
            "customerNum": 426,
            "businessTypeSummaryVoList": [
                {"businessTypeName": "堂食", "actualReceiptAmount": 8000, "orderNum": 200},
                {"businessTypeName": "外卖", "actualReceiptAmount": 3000, "orderNum": 80},
            ],
            "promotionDetailList": [
                {
                    "paySubjectName": "平台券",
                    "promotionDetailInfos": [{"promotionName": "满减券", "actualReceiptAmount": 520}],
                }
            ],
            "dailyCateVo": {"big": "payload"},
        }

        compacted = compact_result("/report/orderBusinessDaily", {"flag": 2, "stime": 20260301, "etime": 20260307}, result)

        self.assertEqual(12888.5, compacted["summary"]["orderAmount"])
        self.assertEqual("堂食", compacted["topBusinessTypesByReceipt"][0]["businessTypeName"])
        self.assertNotIn("dailyCateVo", compacted)
        self.assertNotIn("businessTypeSummaryVoList", compacted)

    def test_compact_order_dimension_stats_list_keeps_sum_and_top_rows(self):
        result = {
            "size": 20,
            "sum": {"orderAmount": 1000, "actualReceiptAmount": 900, "saleOrderNum": 80},
            "list": [
                {"orgName": "门店A", "orderAmount": 600, "actualReceiptAmount": 550, "saleOrderNum": 40, "map": {"1_orderAmount": 300}},
                {"orgName": "门店B", "orderAmount": 400, "actualReceiptAmount": 350, "saleOrderNum": 40, "map": {"1_orderAmount": 200}},
            ],
            "headList": [{"key": "1_orderAmount", "title": "堂食流水"}],
        }

        compacted = compact_result("/report/getOrderDimensionStatsList", {"dimensions": 1, "flag": 2}, result)

        self.assertEqual(1000, compacted["sum"]["orderAmount"])
        self.assertEqual("门店A", compacted["topRows"][0]["name"])
        self.assertEqual(1, compacted["headCount"])
        self.assertNotIn("headList", compacted)

    def test_compact_order_income_stats_list_keeps_sum_and_top_rows(self):
        result = {
            "size": 10,
            "sum": {"orderAmount": 5000, "actualReceiptAmount": 4600, "discountAmount": 400},
            "list": [
                {"orgName": "门店A", "orderAmount": 3000, "actualReceiptAmount": 2800, "discountAmount": 200, "map": {"101_orderAmount": 1500}},
                {"orgName": "门店B", "orderAmount": 2000, "actualReceiptAmount": 1800, "discountAmount": 200, "map": {"101_orderAmount": 900}},
            ],
        }

        compacted = compact_result("/report/getOrderIncomeStatsList", {"flag": 2}, result)

        self.assertEqual(5000, compacted["sum"]["orderAmount"])
        self.assertEqual("门店A", compacted["topRows"][0]["name"])
        self.assertNotIn("list", compacted)

    def test_compact_payment_group_compose_keeps_summary_and_top_groups(self):
        result = {
            "orderNum": 200,
            "actualReceiptAmount": 8000,
            "vipSaleAmount": 500,
            "giftCardSaleAmount": 80,
            "storeAmount": 1200,
            "groupVoList": [
                {
                    "paySubjectGroupName": "现金",
                    "orderNum": 120,
                    "actualReceiptAmount": 5000,
                    "subjectVoList": [{"paySubjectName": "现金", "actualReceiptAmount": 5000, "orderNum": 120}],
                }
            ],
        }

        compacted = compact_result("/report/getPaymentGroupCompose", {"flag": 2}, result)

        self.assertEqual(8000, compacted["summary"]["actualReceiptAmount"])
        self.assertEqual("现金", compacted["topGroups"][0]["paySubjectGroupName"])
        self.assertNotIn("groupVoList", compacted)

    def test_compact_sale_period_summary_keeps_sum_and_top_rows(self):
        result = {
            "size": 8,
            "sum": {"orderAmount": 6000, "actualReceiptAmount": 5600, "saleOrderNum": 240, "customerNum": 300},
            "list": [
                {"timeName": "午市", "orderAmount": 3200, "actualReceiptAmount": 3000, "saleOrderNum": 120, "customerNum": 160},
                {"timeName": "晚市", "orderAmount": 2800, "actualReceiptAmount": 2600, "saleOrderNum": 120, "customerNum": 140},
            ],
            "headList": [{"key": "orderAmount"}],
        }

        compacted = compact_result("/report/salePeriodSummary", {"viewType": 1, "dateType": 1}, result)

        self.assertEqual(6000, compacted["sum"]["orderAmount"])
        self.assertEqual("午市", compacted["topRows"][0]["name"])
        self.assertEqual(1, compacted["headCount"])

    def test_compact_order_shop_ranking_keeps_core_rank_summary(self):
        result = {
            "high": {"orgId": 1, "orgName": "门店A", "orderAmount": 5000, "actualReceiptAmount": 4700, "orderCount": 160},
            "low": {"orgId": 5, "orgName": "门店E", "orderAmount": 900, "actualReceiptAmount": 850, "orderCount": 35},
            "sum": {"orderAmount": 12800, "actualReceiptAmount": 11900, "discountAmount": 900, "traffic": 420, "orderCount": 410},
            "list": [
                {"orgId": 1, "orgName": "门店A", "orderAmount": 5000, "actualReceiptAmount": 4700, "traffic": 180, "orderCount": 160, "discountRate": 0.08},
                {"orgId": 2, "orgName": "门店B", "orderAmount": 3200, "actualReceiptAmount": 3000, "traffic": 120, "orderCount": 110, "discountRate": 0.07},
                {"orgId": 3, "orgName": "门店C", "orderAmount": 2500, "actualReceiptAmount": 2300, "traffic": 80, "orderCount": 90, "discountRate": 0.09},
            ],
            "updateTime": "2026-03-30 10:20:30",
        }

        compacted = compact_result(
            "/report/getOrderShopRanking",
            {"metricsType": 1, "flag": 2, "stime": 20260301, "etime": 20260307, "businessTypeList": [1, 2]},
            result,
        )

        self.assertEqual(1, compacted["request"]["metricsType"])
        self.assertEqual("门店A", compacted["high"]["orgName"])
        self.assertEqual("门店E", compacted["low"]["orgName"])
        self.assertEqual(12800, compacted["sum"]["orderAmount"])
        self.assertEqual("门店A", compacted["topStores"][0]["orgName"])
        self.assertEqual("2026-03-30 10:20:30", compacted["updateTime"])
        self.assertNotIn("list", compacted)

    def test_compact_customer_total_summary_keeps_member_core_fields(self):
        result = {
            "customerCount": 1000,
            "memberCount": 600,
            "consumeMemberCount": 320,
            "rechargeMemberCount": 180,
            "totalRechargeAmount": 80000,
            "totalConsumeBalanceAmount": 45000,
            "totalSedimentaryAmount": 25000,
            "ignoreFiledList": ["totalRechargeAmount"],
        }

        compacted = compact_result("/report/scrm/member/customerTotalSummary", {"orgId": 20001}, result)

        self.assertEqual(600, compacted["summary"]["memberCount"])
        self.assertEqual(["totalRechargeAmount"], compacted["summary"]["ignoreFiledList"])

    def test_compact_org_open_card_member_summary_keeps_top_stores(self):
        result = {
            "size": 20,
            "list": [
                {"orgId": 1, "orgName": "门店A", "memberCount": 55},
                {"orgId": 2, "orgName": "门店B", "memberCount": 40},
            ],
        }

        compacted = compact_result("/report/scrm/member/orgOpenCardMemberSummary", {"flag": 2}, result)

        self.assertEqual(20, compacted["size"])
        self.assertEqual("门店A", compacted["topStores"][0]["orgName"])
        self.assertNotIn("list", compacted)

    def test_compact_org_recharge_member_summary_keeps_top_stores(self):
        result = {
            "size": 20,
            "list": [
                {"orgId": 1, "orgName": "门店A", "rechargeMemberCount": 55, "totalRechargeAmount": 12000},
                {"orgId": 2, "orgName": "门店B", "rechargeMemberCount": 40, "totalRechargeAmount": 9000},
            ],
        }

        compacted = compact_result("/report/scrm/member/orgRechargeMemberSummary", {"flag": 2}, result)

        self.assertEqual(20, compacted["size"])
        self.assertEqual(12000, compacted["topStores"][0]["totalRechargeAmount"])
        self.assertNotIn("list", compacted)


if __name__ == "__main__":
    unittest.main()
