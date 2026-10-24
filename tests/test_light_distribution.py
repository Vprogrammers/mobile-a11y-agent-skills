from pathlib import Path
import json
import tempfile
import unittest

from scripts.build_light_distribution import build
from scripts.validate_light_distribution import main as validate


ROOT = Path(__file__).resolve().parent.parent
SOURCE_COMMIT = "a" * 40


class LightDistributionTests(unittest.TestCase):
    def test_builds_valid_allowlisted_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "light"
            build(ROOT, output, SOURCE_COMMIT)
            self.assertEqual(validate(output), 0)
            self.assertEqual(len(list((output / ".claude/agents").glob("*.md"))), 5)
            self.assertEqual(len(list((output / ".claude/skills").glob("*/SKILL.md"))), 5)
            self.assertFalse((output / "evals").exists())
            self.assertFalse((output / "samples").exists())
            self.assertFalse((output / "scripts").exists())
            self.assertFalse((output / ".github").exists())
            self.assertEqual(json.loads((output / ".source.json").read_text())["source_commit"], SOURCE_COMMIT)

    def test_validator_rejects_unexpected_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "light"
            build(ROOT, output, SOURCE_COMMIT)
            (output / "evals").mkdir()
            self.assertEqual(validate(output), 1)

    def test_validator_rejects_maintainer_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "light"
            build(ROOT, output, SOURCE_COMMIT)
            path = output / ".claude/CLAUDE.md"
            path.write_text(path.read_text() + "\nRun ./scripts/validate.sh\n")
            self.assertEqual(validate(output), 1)


if __name__ == "__main__":
    unittest.main()
