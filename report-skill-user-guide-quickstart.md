# 全来店报表数据技能快速说明

这份文档只保留最重要的几步：

1. 在 OpenClaw 中安装技能
2. 绑定云助手
3. 启用报表助手
4. 开始使用

---

## 一、在 OpenClaw 中安装技能

把下面整段话直接发给 OpenClaw：

```text
请帮我下载安装全来店报表数据技能，并重启服务
https://github.com/liangxu1186-1/openclaw-skills.git
mkdir -p ~/.openclaw/skills
cp -R openclaw-skills/generate_binding_qr ~/.openclaw/skills/
cp -R openclaw-skills/report-skill ~/.openclaw/skills/
cp -R openclaw-skills/setup-report-agent ~/.openclaw/skills/
openclaw gateway restart
```

这段话会让 OpenClaw 自动完成：

1. 下载技能仓库
2. 创建 `~/.openclaw/skills` 目录
3. 安装 `generate_binding_qr`
4. 安装 `report-skill`
5. 安装 `setup-report-agent`
6. 重启 OpenClaw 本地服务

安装完成后，你可以继续对 OpenClaw 说：

```text
请帮我确认全来店报表数据技能是否已经安装成功
```

---

## 二、绑定云助手

安装完技能后，下一步就是绑定云助手。你可以直接对 OpenClaw 说：

```text
请帮我生成云助手绑定二维码
```

或者：

```text
绑定云助手
```

正常情况下，OpenClaw 会直接生成一个二维码。

然后按下面步骤操作：

1. 打开微信
2. 搜索小程序 `全来店云助手`
3. 在小程序里使用扫码功能
4. 扫描 OpenClaw 返回的绑定二维码
5. 完成绑定

注意：

- 二维码有时效，过期后需要重新生成
- 绑定成功后，才能更方便地接收提醒、同步状态或做后续关联操作

如果你不确定是否已经绑定完成，可以继续问：

```text
请帮我确认云助手是否已经绑定成功
```

---

## 三、启用报表助手

这一步是推荐做法。

它的作用很简单：给报表查询单独开一个专用助手，不和你平时闲聊混在同一个会话里。这样通常会更稳，也更不容易越用越慢。

你可以直接把下面这段话发给 OpenClaw：

```text
请使用 setup-report-agent 技能，直接帮我创建 report 报表专用 agent，并重启服务。
不要只介绍功能，不要给我选项。
完成后请明确告诉我：
1. report 是否已经写入 openclaw.json
2. ~/.openclaw/workspace-report 是否已经创建
3. AGENTS.md、SOUL.md、TOOLS.md 是否已经写入
```

正常情况下，OpenClaw 会自动完成这些事：

1. 创建一个专门查报表的 `report` agent
2. 给这个 agent 创建独立 workspace
3. 继承你当前 OpenClaw 默认模型
4. 重启本地服务

你不需要自己懂 agent 配置，只要记住一件事：

- 平时普通聊天，继续用原来的主助手
- 查报表时，切到 `report` 这个报表助手

如果你想确认是否已经启用成功，可以继续说：

```text
请帮我确认 report 报表专用 agent 是否已经创建成功，并告诉我现在能不能在代理列表里看到它
```

---

## 四、开始使用

绑定完成后，就可以直接查报表数据了。

建议先从这些最常用的问题开始：

```text
查询今天营业额
查询本周商品分类销售排行
这个月新增了多少会员
按业务类型查一下
查询支付分组
```

常见可查询内容包括：

- 营业额、实收、优惠、订单数、客流、退款
- 商品销售排行、商品分类销售排行
- 会员总数、新增会员数
- 支付分组 / 支付科目
- 业务类型分析，例如堂食、外卖、退款

为了让结果更准确，提问时尽量把时间说清楚。例如：

```text
查询今天营业额
查询上周商品分类销售排行
查询上月新增会员数
按业务类型看一下今天的数据
```

如果你想让 OpenClaw 帮你判断技能现在是否能正常工作，也可以直接说：

```text
请帮我测试一下全来店报表数据技能是否可以正常使用
```
