#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG = Path("~/.openclaw/openclaw.json").expanduser()
DEFAULT_WORKSPACE = Path("~/.openclaw/workspace-report").expanduser()
DEFAULT_AGENT_ID = "report"


LIGHTWEIGHT_AGENTS_MD = """# AGENTS.md - 报表助手工作区

这个 workspace 只用于报表和经营数据查询。

## 启动规则

1. 默认不要读取长期记忆、日报记忆或无关文档。
2. 用户明确是在查报表时，直接使用报表技能，不要先做无关搜索。
3. 只有当用户明确说“继续上次的报表分析”时，才读取历史上下文。
4. 报表技能固定使用：
   - `~/.openclaw/skills/report-skill/SKILL.md`
   - `~/.openclaw/skills/report-skill/scripts/report_proxy.py`
5. 不要去下面这些路径探测脚本：
   - `~/.openclaw/workspace/skills/report-skill`
   - `~/workspace/scripts/report-skill`
   - 任何通过 `find` / `ls` 猜出来的旧路径

## 回复规则

- 回复以数据为先，简洁直接。
- 优先保持短会话，不要把报表分析拖成长聊天。
- 如果工具输出很大，只提取回答问题所需字段。
- 如果用户问的是普通闲聊、写作或其它非报表问题，提醒切回主助手。
"""


SOUL_MD = """# SOUL.md - 报表助手

你是一个专门负责报表查询和经营数据解读的助手。

## 你的职责

- 快速调用正确的报表接口
- 用普通人能看懂的话解释结果
- 在数据异常时主动提醒风险

## 你的边界

- 不负责长篇闲聊
- 不负责泛化的代码开发任务
- 不负责替用户猜不存在的数据

## 你的风格

- 直接
- 简洁
- 数据优先
- 不绕路

## 核心要求

- 查报表时，固定使用 `~/.openclaw/skills/report-skill`
- 不要自己重新发明报表逻辑
- 不要搜索旧脚本路径
"""


TOOLS_MD = """# TOOLS.md - 报表助手工具说明

## 固定技能路径

- 报表技能：`~/.openclaw/skills/report-skill/SKILL.md`
- 报表脚本：`~/.openclaw/skills/report-skill/scripts/report_proxy.py`

## 使用原则

1. 只要用户是在查经营数据、营业额、商品排行、会员报表、支付分组、业务类型，就优先走报表技能。
2. 默认不要去读旧目录，不要先 `find`、`ls`、`memory_search` 探测脚本位置。
3. 如果用户问的是商品分类销售排行，要优先想到：
   - `dateType`
   - `startDate`
   - `endDate`
   - `viewType`
4. 如果用户问的是营业指标，要优先想到：
   - `flag`
   - `stime`
   - `etime`
   - `period`
   - `viewType`

## 常用脚本命令

```bash
python3 ~/.openclaw/skills/report-skill/scripts/report_proxy.py '/report/getYzsBusinessMetrics' '{"flag":2,"stime":20260330,"etime":20260330,"period":1,"viewType":1}'
```

```bash
python3 ~/.openclaw/skills/report-skill/scripts/report_proxy.py '/report/goodsPosCateSaleSummary' '{"viewType":1,"dateType":2,"startDate":20260330,"endDate":20260330}'
```
"""


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"配置文件不存在: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"配置文件不是合法 JSON: {path}") from exc


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_agent(config: dict, agent_id: str, workspace: Path):
    agents = config.setdefault("agents", {})
    agent_list = agents.setdefault("list", [])
    if not isinstance(agent_list, list):
        raise RuntimeError("openclaw.json 中 agents.list 不是数组")

    existing = None
    for item in agent_list:
        if isinstance(item, dict) and item.get("id") == agent_id:
            existing = item
            break

    created = False
    changed = False

    if existing is None:
        existing = {
            "id": agent_id,
            "workspace": str(workspace),
            "identity": {
                "name": "报表助手",
                "emoji": "📊",
                "theme": "clean analyst",
            },
        }
        agent_list.append(existing)
        created = True
        changed = True
    else:
        if not existing.get("workspace"):
            existing["workspace"] = str(workspace)
            changed = True
        if not isinstance(existing.get("identity"), dict):
            existing["identity"] = {
                "name": "报表助手",
                "emoji": "📊",
                "theme": "clean analyst",
            }
            changed = True
        else:
            identity = existing["identity"]
            if not identity.get("name"):
                identity["name"] = "报表助手"
                changed = True
            if not identity.get("emoji"):
                identity["emoji"] = "📊"
                changed = True
            if not identity.get("theme"):
                identity["theme"] = "clean analyst"
                changed = True

    return created, changed, existing


def ensure_workspace(workspace: Path):
    workspace.mkdir(parents=True, exist_ok=True)
    created = {
        "AGENTS.md": False,
        "SOUL.md": False,
        "TOOLS.md": False,
    }

    files = {
        "AGENTS.md": LIGHTWEIGHT_AGENTS_MD,
        "SOUL.md": SOUL_MD,
        "TOOLS.md": TOOLS_MD,
    }

    for name, content in files.items():
        path = workspace / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created[name] = True

    return created


def report_skill_installed(state_dir: Path):
    return (state_dir / "skills" / "report-skill" / "SKILL.md").exists()


def restart_gateway():
    completed = subprocess.run(
        ["openclaw", "gateway", "restart"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ok": completed.returncode == 0,
        "code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main():
    parser = argparse.ArgumentParser(description="Create or repair a dedicated OpenClaw report agent")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to openclaw.json")
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="Workspace directory for the report agent")
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID, help="Agent id to create or repair")
    parser.add_argument("--no-restart", action="store_true", help="Do not restart the gateway after updating config")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()
    workspace = Path(args.workspace).expanduser()
    state_dir = config_path.parent

    config = load_json(config_path)
    created, changed, agent = ensure_agent(config, args.agent_id, workspace)
    workspace_created = ensure_workspace(workspace)

    if changed:
        write_json(config_path, config)

    restart = None
    if not args.no_restart and changed:
        restart = restart_gateway()

    payload = {
        "ok": True,
        "agentId": args.agent_id,
        "created": created,
        "configChanged": changed,
        "workspace": str(workspace),
        "workspaceCreated": workspace_created,
        "modelPinned": bool(agent.get("model")),
        "inheritsDefaultModel": not bool(agent.get("model")),
        "reportSkillInstalled": report_skill_installed(state_dir),
        "gatewayRestart": restart,
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
