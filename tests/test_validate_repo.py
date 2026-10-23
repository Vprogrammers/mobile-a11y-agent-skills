from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parent.parent


class ValidateRepositoryTests(unittest.TestCase):
    def test_repository_is_valid(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validate_repo.py", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
