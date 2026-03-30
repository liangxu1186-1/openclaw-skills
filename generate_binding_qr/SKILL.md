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
2. 优先运行 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown`，脚本会直接输出适合 OpenClaw / WebChat / Control UI 渲染的完整 Markdown，并使用标准 Markdown 图片语法承载 `data:image/png;base64,...`；如果只需要原始图片 data URL，再使用默认输出。
3. 如需显式传入公钥，使用 `python3 {baseDir}/scripts/qr_binding_skill.py --format markdown --public-key "<公钥>"`。
4. 脚本首次运行时若检测到缺少 Python 依赖，会自动执行 `python3 -m pip install --user --default-timeout 120 --retries 5 -r {baseDir}/requirements.txt` 补齐依赖，然后继续执行。
5. 如果脚本默认输出的是完整 Markdown，直接原样返回；不要再额外包 `<img>` HTML 标签，也不要改写成 `MEDIA:` 行。
6. 如果脚本返回错误字符串，不要伪造二维码，直接按异常处理规则回复。

## 输出要求
优先直接返回脚本在 `--format markdown` 下生成的完整 Markdown。
如果脚本只返回图片 data URL，再使用如下格式：

### 绑定您的云助手
生成完成后，请使用微信搜索 **“云助手”** 小程序，或直接打开小程序后点击扫码功能，扫描下方二维码完成绑定：

![扫码绑定]({{generate_binding_qr_output}})

安全提示：此二维码包含当前实例唯一身份标识，请勿发送给陌生人。二维码有效期为 5 分钟。

## 预热与健康检查
- 健康检查：`python3 ./scripts/qr_binding_skill.py --healthcheck --trace`
- 预热（内存生成小图）：`python3 ./scripts/qr_binding_skill.py --warmup --trace`
- 可配合统一预热脚本：`python3 ../../scripts/warmup_skills.py --trace`

## 异常处理
- 如果脚本返回“未找到公钥”，提示用户检查服务器 `keys/` 目录中的密钥文件是否存在，或显式传入 `--public-key`。
- 如果脚本自动安装依赖失败，提示用户检查宿主机网络、Python `pip` 可用性，以及当前账号是否允许写入用户 site-packages；当前依赖已简化为纯 Python 的 `qrcode[png]`，无需 `Pillow`。
- 如果二维码生成失败，提示用户稍后重试，或改为手动输入公钥进行绑定。
