from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class InstallSmokeTests(unittest.TestCase):
    def test_copy_install_layout(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/install_smoke.py", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_copy_install_rejects_missing_skill_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "repo"
            shutil.copytree(
                ROOT,
                copy,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".gradle", ".kotlin", "build", ".build", ".swiftpm", "DerivedData"
                ),
            )
            (copy / "skills/mobile-a11y-testing/references/test-matrix.md").unlink()
            result = subprocess.run(
                ["python3", str(ROOT / "scripts/install_smoke.py"), str(copy)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing local links", result.stdout)


if __name__ == "__main__":
    unittest.main()
