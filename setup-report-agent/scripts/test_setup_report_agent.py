import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setup_report_agent import ensure_workspace


class SetupReportAgentTest(unittest.TestCase):

    def test_ensure_workspace_removes_stale_template_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "IDENTITY.md").write_text("stale identity", encoding="utf-8")
            (workspace / "USER.md").write_text("stale user", encoding="utf-8")

            result = ensure_workspace(workspace)

            self.assertTrue((workspace / "AGENTS.md").exists())
            self.assertTrue((workspace / "SOUL.md").exists())
            self.assertTrue((workspace / "TOOLS.md").exists())
            self.assertFalse((workspace / "IDENTITY.md").exists())
            self.assertFalse((workspace / "USER.md").exists())
            self.assertIn("IDENTITY.md", result["removed"])
            self.assertIn("USER.md", result["removed"])

    def test_ensure_workspace_writes_brief_answer_instruction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            ensure_workspace(workspace)

            agents_md = (workspace / "AGENTS.md").read_text(encoding="utf-8")
            tools_md = (workspace / "TOOLS.md").read_text(encoding="utf-8")

            self.assertIn("briefCn", agents_md)
            self.assertIn("riskHints", agents_md)
            self.assertIn("不要重新拼大表", agents_md)
            self.assertIn("briefCn", tools_md)
            self.assertIn("riskHints", tools_md)


if __name__ == "__main__":
    unittest.main()
