import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compactors import compact_result


class CompactorsRegistryTest(unittest.TestCase):

    def test_compactors_package_compacts_member_period_summary_with_period_aliases(self):
        result = {
            "customerCount": 3,
            "memberCount": 2,
            "cardCount": 2,
            "consumeMemberCount": 5,
            "rechargeMemberCount": 5,
            "orderAmount": 15488.33,
            "orderNum": 6,
            "totalRechargeAmount": 26728.06,
            "totalConsumeBalanceAmount": 6865.47,
            "totalSedimentaryAmount": 19662.58,
            "upCustomerCount": 0,
            "upMemberCount": 1,
            "upCardCount": 1,
            "upConsumeMemberCount": 3,
            "upRechargeMemberCount": 4,
            "upOrderAmount": 7000.12,
            "upOrderNum": 4,
            "chainMemberRate": 100,
            "chainRechargeAmountRate": 100,
        }

        compacted = compact_result(
            "/report/scrm/member/customerPeriodSummary",
            {"flag": 2, "stime": 20260301, "etime": 20260330, "period": 3},
            result,
        )

        self.assertEqual(2, compacted["current"]["newMemberCount"])
        self.assertEqual(2, compacted["current"]["newCardCount"])
        self.assertNotIn("memberCount", compacted["current"])
        self.assertEqual(1, compacted["previous"]["newMemberCount"])
        self.assertEqual(1, compacted["previous"]["newCardCount"])
        self.assertEqual(100, compacted["rates"]["chainMemberRate"])

    def test_compactors_package_compacts_member_period_summary_with_metrics_list(self):
        result = {
            "customerCount": 3,
            "memberCount": 2,
            "cardCount": 2,
            "consumeMemberCount": 5,
            "rechargeMemberCount": 5,
            "orderAmount": 15488.33,
            "orderNum": 6,
            "totalRechargeAmount": 26728.06,
            "totalConsumeBalanceAmount": 6865.47,
            "totalSedimentaryAmount": 19662.58,
            "upCustomerCount": 1,
            "upMemberCount": 1,
            "upCardCount": 1,
            "upConsumeMemberCount": 3,
            "upRechargeMemberCount": 4,
            "upOrderAmount": 7000.12,
            "upOrderNum": 4,
        }

        compacted = compact_result(
            "/report/scrm/member/customerPeriodSummary",
            {"flag": 2, "stime": 20260301, "etime": 20260330, "period": 3},
            result,
        )

        metrics_by_label = {item["label"]: item for item in compacted["metrics"]}

        self.assertEqual(2, metrics_by_label["新增会员数"]["current"])
        self.assertEqual(1, metrics_by_label["新增会员数"]["previous"])
        self.assertEqual(15488.33, metrics_by_label["期间订单金额"]["current"])
        self.assertEqual(2, metrics_by_label["新增办卡数"]["current"])

    def test_compactors_package_compacts_order_shop_ranking(self):
        result = {
            "high": {"orgId": 1, "orgName": "门店A", "orderAmount": 5000},
            "low": {"orgId": 5, "orgName": "门店E", "orderAmount": 900},
            "sum": {"orderAmount": 12800, "actualReceiptAmount": 11900},
            "list": [
                {"orgId": 1, "orgName": "门店A", "orderAmount": 5000},
                {"orgId": 2, "orgName": "门店B", "orderAmount": 3200},
            ],
            "updateTime": "2026-03-30 10:20:30",
        }

        compacted = compact_result(
            "/report/getOrderShopRanking",
            {"metricsType": 1, "flag": 2, "stime": 20260301, "etime": 20260307},
            result,
        )

        self.assertEqual(1, compacted["request"]["metricsType"])
        self.assertEqual("门店A", compacted["high"]["orgName"])
        self.assertEqual("门店A", compacted["topStores"][0]["orgName"])
        self.assertEqual("2026-03-30 10:20:30", compacted["updateTime"])


if __name__ == "__main__":
    unittest.main()
