from compactors.common import compact_rank_summary, pick_fields


def build_member_period_metrics(result):
    return [
        {"label": "新增客户数", "current": result.get("customerCount"), "previous": result.get("upCustomerCount"), "rateField": "chainCustomerRate"},
        {"label": "新增会员数", "current": result.get("memberCount"), "previous": result.get("upMemberCount"), "rateField": "chainMemberRate"},
        {"label": "新增办卡数", "current": result.get("cardCount"), "previous": result.get("upCardCount"), "rateField": "chainCardRate"},
        {"label": "期间消费会员数", "current": result.get("consumeMemberCount"), "previous": result.get("upConsumeMemberCount"), "rateField": "chainConsumeCountRate"},
        {"label": "期间充值会员数", "current": result.get("rechargeMemberCount"), "previous": result.get("upRechargeMemberCount"), "rateField": "chainRechargeCountRate"},
        {"label": "期间订单金额", "current": result.get("orderAmount"), "previous": result.get("upOrderAmount")},
        {"label": "期间订单数", "current": result.get("orderNum"), "previous": result.get("upOrderNum"), "rateField": "chainOrderNumRate"},
        {"label": "期间充值金额", "current": result.get("totalRechargeAmount"), "previous": result.get("upTotalRechargeAmount"), "rateField": "chainRechargeAmountRate"},
        {
            "label": "期间消费余额",
            "current": result.get("totalConsumeBalanceAmount"),
            "previous": result.get("upTotalConsumeBalanceAmount"),
            "rateField": "chainTotalConsumeBalanceAmountRate",
        },
        {
            "label": "期间沉淀金额",
            "current": result.get("totalSedimentaryAmount"),
            "previous": result.get("upTotalSedimentaryAmount"),
            "rateField": "chainTotalSedimentaryAmountRate",
        },
    ]


def compact_member_period_summary(result, payload):
    if not isinstance(result, dict):
        return result

    return {
        "request": pick_fields(payload or {}, ["flag", "stime", "etime", "period", "viewType"]),
        "metrics": build_member_period_metrics(result),
        "current": {
            "newCustomerCount": result.get("customerCount"),
            "newMemberCount": result.get("memberCount"),
            "newCardCount": result.get("cardCount"),
            "periodConsumeMemberCount": result.get("consumeMemberCount"),
            "periodRechargeMemberCount": result.get("rechargeMemberCount"),
            "periodOrderAmount": result.get("orderAmount"),
            "periodOrderNum": result.get("orderNum"),
            "periodRechargeAmount": result.get("totalRechargeAmount"),
            "periodConsumeBalanceAmount": result.get("totalConsumeBalanceAmount"),
            "periodSedimentaryAmount": result.get("totalSedimentaryAmount"),
        },
        "previous": {
            "newCustomerCount": result.get("upCustomerCount"),
            "newMemberCount": result.get("upMemberCount"),
            "newCardCount": result.get("upCardCount"),
            "periodConsumeMemberCount": result.get("upConsumeMemberCount"),
            "periodRechargeMemberCount": result.get("upRechargeMemberCount"),
            "periodOrderAmount": result.get("upOrderAmount"),
            "periodOrderNum": result.get("upOrderNum"),
        },
        "rates": pick_fields(
            result,
            [
                "chainCustomerRate",
                "chainMemberRate",
                "chainConsumeCountRate",
                "chainRechargeAmountRate",
                "chainTotalConsumeBalanceAmountRate",
                "chainTotalSedimentaryAmountRate",
            ],
        ),
    }


def compact_customer_total_summary(result, payload):
    if not isinstance(result, dict):
        return result

    return {
        "request": pick_fields(payload or {}, ["orgId", "orgIdList", "brandIdList", "isStudentMember", "isNotContainsGiveMoney"]),
        "summary": pick_fields(
            result,
            [
                "customerCount",
                "consumeCustomerCount",
                "cardCount",
                "memberCount",
                "consumeMemberCount",
                "rechargeMemberCount",
                "totalRechargeAmount",
                "totalBalance",
                "totalConsumeBalanceAmount",
                "totalSedimentaryAmount",
                "totalSedimentaryRate",
                "changeMemberRate",
                "changeConsumeRate",
                "changeRechargeRate",
                "ignoreFiledList",
            ],
        ),
    }


def build_member_registry():
    return {
        "/report/scrm/member/customerTotalSummary": lambda payload, result: compact_customer_total_summary(result, payload),
        "/report/scrm/member/customerPeriodSummary": lambda payload, result: compact_member_period_summary(result, payload),
        "/report/scrm/member/orgOpenCardMemberSummary": lambda payload, result: compact_rank_summary(
            result,
            payload,
            ["flag", "stime", "etime", "dataNum", "pageNo"],
            ["orgId", "orgName", "memberCount"],
            "memberCount",
        ),
        "/report/scrm/member/orgRechargeMemberSummary": lambda payload, result: compact_rank_summary(
            result,
            payload,
            ["flag", "stime", "etime", "groupKey", "pageNo"],
            ["orgId", "orgName", "rechargeMemberCount", "totalRechargeAmount", "totalRechargeMoneyAmount", "totalRechargeGiveAmount"],
            "totalRechargeAmount",
        ),
    }
