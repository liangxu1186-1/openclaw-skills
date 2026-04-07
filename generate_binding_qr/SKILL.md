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
- 连接小程序
- 关联云助手
- 扫码绑定
- 生成二维码

## 执行逻辑
1. 确认用户要进行云助手绑定。
2. 优先运行 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown`，直接输出完整二维码 Markdown。
3. 如需显式传入公钥，使用 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown --public-key "<公钥>"`。
4. 脚本会解析当前 OpenClaw 公钥，请求服务端 `/report/openclaw/binding/qr-image` 获取远程二维码图片 URL，再下载 PNG 并转换成 `data:image/png;base64,...`。
5. 如果脚本输出的是完整回复文本，最终回复必须只包含该 stdout，并且逐字符原样返回：
   - 不要增删任何字符
   - 不要添加标题、后记或安全提示
   - 不要做摘要，不要改写措辞
   - 不要把 Markdown 包进代码块
6. 生成二维码必须作为这一轮的最后一步。不要在二维码生成之后继续调用其他 tool，也不要在二维码 Markdown 前后追加任何说明文字，否则 Control UI 可能只显示文本总结而不显示图片。
7. 如果同一轮里还有别的事情要做，例如更新记忆、修改文件、查询状态，必须先做完，再最后单独生成二维码并结束回复。
8. 如果脚本返回错误字符串或非 0 退出，不要伪造二维码，不要自行脑补“服务未运行”之类结论；必须基于脚本 stdout/stderr 中的真实错误回复。

## 输出要求
优先直接返回脚本在 `--format markdown` 下生成的完整回复，并且整条 assistant 最终回复只包含这段 stdout。
脚本成功时，stdout 应当只包含两行：

请在5分钟内使用云助手小程序扫码绑定
![扫码绑定](data:image/png;base64,...)

## 预热与健康检查
- 健康检查：`python3 ./scripts/qr_binding_skill.py --healthcheck --trace`
- 预热（检查公钥和二维码接口地址）：`python3 ./scripts/qr_binding_skill.py --warmup --trace`
- 可配合统一预热脚本：`python3 ../../scripts/warmup_skills.py --trace`

## 异常处理
- 如果脚本返回“未找到公钥”，提示用户检查服务器 `keys/` 目录中的密钥文件是否存在，或显式传入 `--public-key`。
- 如果脚本调用二维码图片接口失败，优先原样转述脚本里给出的请求地址、状态码或底层异常，再提示用户检查 `SAAS_API_URL`、服务端接口是否已部署，以及当前公钥是否有效。
- 如果二维码图片生成失败，提示用户稍后重试，或改为手动输入公钥进行绑定。
