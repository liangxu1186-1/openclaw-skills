`report-skill` 的会员域接口目录。

会员域当前保留 2 个 `/agent/member/...` 接口，已全部实现。

## 已实现接口

1. `/agent/member/overview`
   适用问题：会员总数、新增会员、开卡、充值等会员总览。
   详细字段：[../schema/agent/memberOverview.md](../schema/agent/memberOverview.md)

2. `/agent/member/preference`
   适用问题：会员最喜爱商品、会员消费门店、会员消费门店排行、会员口味偏好。
   详细字段：[../schema/agent/memberPreference.md](../schema/agent/memberPreference.md)

## 使用规则

- 会员域接口统一只传 `startTime`、`endTime`、`flag`
- 会员域查询时间范围不能超过 `90` 天
- `member/preference` 保持一个接口返回三块数据，不拆成三个 tool call
- `member/overview` 返回会员总量和区间新增/开卡/充值/消费会员数
- “会员消费门店排行”统一通过 `member/preference` 的 `favoriteStores` 回答
- 当前不再提供独立的 `/agent/member/ranking` 接口
- 默认回答保持简短，只给结论和少量关键点，不展开成长段分析
