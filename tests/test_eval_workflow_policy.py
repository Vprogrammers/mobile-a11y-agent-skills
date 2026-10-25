from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/eval-regression.yml"


class EvalWorkflowPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_oauth_workflow_does_not_use_bare_mode(self) -> None:
        self.assertIn("CLAUDE_CODE_OAUTH_TOKEN", self.workflow)
        self.assertNotIn("--bare", self.workflow)

    def test_agent_loads_plugin_and_selected_agent(self) -> None:
        self.assertIn('--plugin-dir "{plugin_dir}"', self.workflow)
        self.assertIn("--agent mobile-a11y-agent-skills:{agent}", self.workflow)

    def test_commands_are_bounded_and_ephemeral(self) -> None:
        self.assertEqual(self.workflow.count("--max-budget-usd"), 2)
        self.assertEqual(self.workflow.count("--max-turns"), 2)
        self.assertEqual(self.workflow.count("--no-session-persistence"), 2)

    def test_agent_and_judge_use_independent_models(self) -> None:
        self.assertIn("claude -p --model sonnet", self.workflow)
        self.assertIn("claude -p --model opus", self.workflow)
        self.assertIn("EVAL_MODEL: agent=sonnet,judge=opus", self.workflow)

    def test_official_eval_keeps_baseline_and_cost_cap(self) -> None:
        self.assertIn("--ablation with-without", self.workflow)
        self.assertIn("--max-cost-usd 8.00", self.workflow)

    def test_paid_evals_run_only_on_demand(self) -> None:
        self.assertNotIn("schedule:", self.workflow)
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("GITHUB_STEP_SUMMARY", self.workflow)


if __name__ == "__main__":
    unittest.main()
