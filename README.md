# OpenClaw Skills

这个仓库用于半正式分发多个 OpenClaw skill，适合通过 GitHub 仓库安装：

- `generate_binding_qr`
- `report-skill`
- `setup-report-agent`

这条分发方式不依赖 ClawHub，用户手动复制到本机 skill 目录即可使用。

## 安装方式

先克隆仓库，再把一个或两个 skill 目录复制到共享 skill 目录：

```bash
git clone https://github.com/<your-org>/openclaw-skills.git
mkdir -p ~/.openclaw/skills
cp -R openclaw-skills/generate_binding_qr ~/.openclaw/skills/
cp -R openclaw-skills/report-skill ~/.openclaw/skills/
cp -R openclaw-skills/setup-report-agent ~/.openclaw/skills/
openclaw gateway restart
openclaw skills list
```

如果只想安装其中一个，就只复制对应目录。

## 技能说明

### `generate_binding_qr`

为当前 OpenClaw 实例生成云助手绑定二维码。

依赖：

- Python 3
- `qrcode[png]`

脚本首次运行时会自动尝试安装依赖。

### `report-skill`

通过 OpenClaw bridge 调用 SaaS 报表接口，并基于返回数据做简短经营分析。

依赖：

- Python 3
- `requests`

脚本内置了默认测试域名，也支持通过 `SAAS_API_URL` 环境变量覆盖：

```bash
export SAAS_API_URL="https://your-saas-host.example.com"
```

skill 会自动拼接 `/report/openclaw/bridge`，不需要手动补这个前缀。

### `setup-report-agent`

为普通用户创建一个独立的 `report` agent，用于把报表查询和日常聊天拆开。

特点：

- 不写死模型，默认继承用户当前 OpenClaw 的默认模型
- 自动创建 `~/.openclaw/workspace-report`
- 自动写入轻量版 `AGENTS.md`
- 自动重启 `openclaw gateway`

典型用法：

```text
请帮我启用报表专用助手
```

## 更新方式

拉取最新代码后，覆盖本机 skill 目录并重启 gateway：

```bash
git pull
cp -R generate_binding_qr ~/.openclaw/skills/
cp -R report-skill ~/.openclaw/skills/
cp -R setup-report-agent ~/.openclaw/skills/
openclaw gateway restart
```
