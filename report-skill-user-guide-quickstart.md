# 全来店报表助手快速说明

这份文档只给普通用户看。

你不用自己打开终端执行命令，但发给 OpenClaw 的内容里要带上明确命令。这样它更容易一次执行成功，不会自己猜路径。

---

## 一、安装报表技能

新开会话，把这段话直接发给 OpenClaw：

```text
请严格按下面命令安装全来店报表相关技能，不要省略步骤，不要改写命令；安装完成后重启服务，并明确告诉我是否安装成功：
https://github.com/liangxu1186-1/openclaw-skills.git
rm -rf /tmp/openclaw-skills-quickstart
git clone https://github.com/liangxu1186-1/openclaw-skills.git /tmp/openclaw-skills-quickstart
mkdir -p ~/.openclaw/skills
cp -R /tmp/openclaw-skills-quickstart/generate_binding_qr ~/.openclaw/skills/
cp -R /tmp/openclaw-skills-quickstart/report-skill ~/.openclaw/skills/
cp -R /tmp/openclaw-skills-quickstart/setup-report-agent ~/.openclaw/skills/
openclaw gateway restart
如果安装失败，请明确告诉我失败原因，不要只说已经完成。
```

安装成功后，再发一句：

```text
请帮我确认全来店报表相关技能是否已经安装成功，并告诉我下面这些检查结果：
1. ~/.openclaw/skills/generate_binding_qr 是否存在
2. ~/.openclaw/skills/report-skill 是否存在
3. ~/.openclaw/skills/setup-report-agent 是否存在
4. gateway 是否已经重启成功
```

---

## 二、绑定云助手

把这段话直接发给 OpenClaw：

```text
请帮我生成云助手绑定二维码。
请直接执行绑定二维码 skill，不要只回复说明文字。
如果二维码生成成功，请直接把二维码显示出来，不要只回复文字说明。
```

看到二维码后：

1. 打开微信
2. 搜索小程序 `全来店云助手`
3. 打开小程序后使用扫码功能
4. 扫描 OpenClaw 返回的二维码
5. 完成绑定

如果二维码过期，就再发一次：

```text
请重新生成云助手绑定二维码。
```

---

## 三、启用报表助手

把这段话直接发给 OpenClaw：

```text
请严格按下面步骤启用报表助手，不要只介绍功能，不要给我选项：
1. 先确认 ~/.openclaw/skills/setup-report-agent/scripts/setup_report_agent.py 是否存在
2. 然后直接执行：
python3 ~/.openclaw/skills/setup-report-agent/scripts/setup_report_agent.py
3. 如果脚本执行成功，再执行：
openclaw gateway restart
完成后请明确告诉我：
1. report 是否已经写入 openclaw.json
2. ~/.openclaw/workspace-report 是否已经创建
3. AGENTS.md、SOUL.md、TOOLS.md 是否已经写入
4. 我现在是否可以开始使用报表助手
如果失败，请直接告诉我失败原因。
```

如果你想继续确认一次，再发一句：

```text
请帮我确认 report 报表专用 agent 是否已经创建成功，并告诉我下面这些检查结果：
1. openclaw agents list 里是否已经有 report
2. ~/.openclaw/workspace-report 是否存在
3. ~/.openclaw/workspace-report/AGENTS.md 是否存在
4. ~/.openclaw/workspace-report/SOUL.md 是否存在
5. ~/.openclaw/workspace-report/TOOLS.md 是否存在
```

---

## 四、开始使用

启用完成后，就可以直接问这些问题：

```text
查询今天营业额
查询本周商品分类销售排行
这个月新增了多少会员
按业务类型查一下
查询支付分组
```

提问时，尽量把时间说清楚，例如：

```text
查询今天营业额
查询上周商品分类销售排行
查询上月新增会员数
按业务类型看一下今天的数据
查询这个月的门店榜单
```

如果你想确认现在整套能力是否可用，可以直接发：

```text
请帮我测试全来店报表助手现在是否可以正常使用，并告诉我哪一步还有问题。
```
