---
name: setup-report-agent
description: 当用户想创建、启用或重建一个专门用于报表查询的 OpenClaw agent 时使用；适合处理“启用报表助手”“创建报表专用 agent”“给我单独做一个查报表的助手”等请求。
---

## 功能
为当前 OpenClaw 实例创建一个独立的 `report` agent，用于承接报表查询，避免和日常聊天共用同一条肥会话。

## 强制要求
1. 只要用户是在说“启用报表专用助手”“创建报表 agent”“重建报表助手”，就必须先执行 `setup_report_agent.py`。
2. 没有执行脚本、没有写入 `openclaw.json`、没有创建 `workspace-report`，都不能算完成。
3. 严禁只根据已有知识回复“已经就绪”“我可以直接帮你查”，也严禁把这类请求误当成普通报表查询。
4. 这类请求的目标是“创建独立 agent”，不是“直接调用 report-analytics 技能查数据”。

## 适用场景
当用户表达以下意图时使用本技能：

- 启用报表专用助手
- 创建报表 agent
- 单独做一个查报表的助手
- 给报表查询单独开一个 agent
- 重建报表助手

## 执行逻辑
1. 优先运行：

   ```bash
   python3 {baseDir}/scripts/setup_report_agent.py
   ```

   不要先解释，不要先给选项，不要先介绍已有报表能力。先执行脚本，再汇报结果。

2. 脚本默认会：
   - 在 `~/.openclaw/openclaw.json` 中创建或补全 `report` agent
   - 创建 `~/.openclaw/workspace-report`
   - 写入中文的 `AGENTS.md`、`SOUL.md`、`TOOLS.md`
   - 在这些文件里明确指向 `~/.openclaw/skills/report-skill`
   - 不显式指定模型，继承用户当前默认模型配置
   - 重启 `openclaw gateway`

3. 如果用户明确要求使用其它 agent id 或 workspace，可追加参数：

   ```bash
   python3 {baseDir}/scripts/setup_report_agent.py --agent-id analytics --workspace ~/.openclaw/workspace-analytics
   ```

4. 不要为普通用户自动绑定整个渠道到 `report` agent，除非用户明确要求。默认只创建 agent，不改渠道路由。
5. 如果脚本返回成功摘要，最终回复用简短中文说明：
   - 已创建或已检查 `report` agent
   - 没有写死模型
   - 后续应在 Control UI 中切换到 `report` agent 使用
6. 如果脚本没有执行，任务就还没完成。不要输出“已经启用”“已经就绪”这类结论。

## 输出要求
1. 不要长篇解释 OpenClaw 架构，只告诉用户：
   - 是否已创建成功
   - agent id 是什么
   - workspace 在哪里
   - 是否已写入 `AGENTS.md`、`SOUL.md`、`TOOLS.md`
   - 该 agent 会继承默认模型
   - 如何开始使用
2. 如果用户原话接近“请帮我启用报表专用助手”，最终回复里必须包含这些明确事实：
   - `report` 是否真的已写入 `openclaw.json`
   - `~/.openclaw/workspace-report` 是否真的已创建
   - gateway 是否已重启
   - 如果还没创建成功，要明确说“尚未创建成功”，不能模糊表达
3. 如果脚本提示 agent 已存在，不要当成错误，直接说明“已存在，已补齐缺失配置”。
4. 如果用户还没有安装 `report-skill`，要明确提醒先安装 `report-skill`，否则新 agent 虽然能创建，但无法查报表。

## 异常处理
1. 如果脚本提示 `openclaw.json` 不存在或 JSON 非法，直接告诉用户当前 OpenClaw 配置异常，需要先修复配置文件。
2. 如果 gateway 重启失败，告诉用户 agent 配置已经写入，但需要手动执行：

   ```bash
   openclaw gateway restart
   ```

3. 如果权限不足导致无法写入 `~/.openclaw`，明确告诉用户当前环境不允许修改 OpenClaw 本地配置。
