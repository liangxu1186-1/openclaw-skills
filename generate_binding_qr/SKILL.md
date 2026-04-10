---
name: generate-binding-qr
description: 当用户想生成云助手绑定二维码、扫码绑定、连接或关联云助手小程序时使用。
---

## 功能
本技能用于为当前 OpenClaw 实例生成云助手绑定二维码，方便用户通过扫码完成实名绑定、多端同步和消息提醒。

## 触发条件
当用户表达以下意图时使用本技能：
- 绑定云助手
- 开始绑定
- 解绑云助手
- 解除绑定
- 取消绑定
- 连接小程序
- 关联云助手
- 扫码绑定
- 扫码解绑
- 生成二维码

## 执行逻辑
1. 确认用户要进行云助手绑定。
2. 优先运行 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown`，直接输出完整二维码 Markdown。
3. 如需显式传入绑定标识，使用 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown --identity "<标识值>"`。
4. 若用户意图是“解绑 / 解除绑定 / 取消绑定 / 扫码解绑”，运行 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown --bind-type 0`；其余绑定类意图保持默认 `--bind-type 1`。
5. 脚本会优先读取 `OPENCLAW_IDENTITY`；云端单用户场景下，其次读取 `/home/gem/workspace/agent/openclaw.json` 中 `channels.feishu.appId + allowFrom[0]`，并规范成 `feishu-owner:{appId}:{openId}`；否则读取 `~/.openclaw/identity/device.json` 中的 `deviceId`；最后兜底读取 `/home/gem/workspace/agent/identity/device.json`，并继续用请求参数名 `publicKey` 调用服务端 `/report/openclaw/binding/qr-image` 获取远程二维码图片 URL，再下载 PNG 并转换成 `data:image/png;base64,...`。
6. 如果脚本输出的是完整回复文本，最终回复必须只包含该 stdout，并且逐字符原样返回：
   - 不要增删任何字符
   - 不要添加标题、后记或安全提示
   - 不要做摘要，不要改写措辞
   - 不要把 Markdown 包进代码块
7. 生成二维码必须作为这一轮的最后一步。不要在二维码生成之后继续调用其他 tool，也不要在二维码 Markdown 前后追加任何说明文字，否则 Control UI 可能只显示文本总结而不显示图片。
8. 如果同一轮里还有别的事情要做，例如更新记忆、修改文件、查询状态，必须先做完，再最后单独生成二维码并结束回复。
9. 如果脚本返回错误字符串或非 0 退出，不要伪造二维码，不要自行脑补“服务未运行”之类结论；必须基于脚本 stdout/stderr 中的真实错误回复。

## 输出要求
优先直接返回脚本在 `--format markdown` 下生成的完整回复，并且整条 assistant 最终回复只包含这段 stdout。
脚本成功时，stdout 应当只包含两行：

请在10分钟内使用云助手小程序扫码绑定
![扫码绑定](data:image/png;base64,...)

解绑时应改为：

请在10分钟内使用云助手小程序扫码解绑
![扫码解绑](data:image/png;base64,...)

## 预热与健康检查
- 健康检查：`python3 ./scripts/qr_binding_skill.py --healthcheck --trace`
- 预热（检查标识和二维码接口地址）：`python3 ./scripts/qr_binding_skill.py --warmup --trace`
- 可配合统一预热脚本：`python3 ../../scripts/warmup_skills.py --trace`

## 异常处理
- 如果脚本返回“未找到标识”，提示用户检查 `OPENCLAW_IDENTITY`、`/home/gem/workspace/agent/openclaw.json`、`~/.openclaw/identity/device.json` 或 `/home/gem/workspace/agent/identity/device.json` 是否存在有效值，或显式传入 `--identity`。
- 如果脚本调用二维码图片接口失败，优先原样转述脚本里给出的请求地址、状态码或底层异常，再提示用户检查 `SAAS_API_URL`、服务端接口是否已部署，以及当前标识值是否有效。
- 如果二维码图片生成失败，提示用户稍后重试，或改为手动输入标识值进行绑定。
