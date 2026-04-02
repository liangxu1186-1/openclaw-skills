`report-skill` 的商品域接口目录。

商品域当前提供 6 个 `/agent/goods/...` 接口，已全部实现。

## 已实现接口

1. `/agent/goods/overview`
   适用问题：商品销售统计金额相关数据。
   字段说明：[../schema/agent/goodsOverview.md](../schema/agent/goodsOverview.md)

2. `/agent/goods/sales-ranking`
   适用问题：商品销售排行。
   字段说明：[../schema/agent/goodsSalesRanking.md](../schema/agent/goodsSalesRanking.md)

3. `/agent/goods/category-ranking`
   适用问题：销售分类排行。
   字段说明：[../schema/agent/goodsCategoryRanking.md](../schema/agent/goodsCategoryRanking.md)

4. `/agent/goods/refund-ranking`
   适用问题：商品退货排行。
   字段说明：[../schema/agent/goodsRefundRanking.md](../schema/agent/goodsRefundRanking.md)

5. `/agent/goods/gift-ranking`
   适用问题：商品赠送排行。
   字段说明：[../schema/agent/goodsGiftRanking.md](../schema/agent/goodsGiftRanking.md)

6. `/agent/goods/income-subject`
   适用问题：商品收入科目统计、收入科目构成。
   字段说明：[../schema/agent/goodsIncomeSubject.md](../schema/agent/goodsIncomeSubject.md)

## 使用规则

- 商品域所有接口统一只传 `startTime`、`endTime`、`flag`
- 商品域查询时间范围不能超过 `183` 天
- 商品类接口的具体排行、分组、统计维度由后端 facade 内部转换，skill 不再直接理解 legacy 参数
- `goods/income-subject` 返回固定 `items` 列表，不再暴露 legacy 动态表头和 `map`
- `goods/income-subject` 每项当前只关心 `incomeSubjectId`、`incomeSubjectName`、`orderAmount`、`actualReceiptAmount`、`discountAmount`
