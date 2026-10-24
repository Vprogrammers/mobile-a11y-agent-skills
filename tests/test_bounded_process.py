from __future__ import annotations

import sys
import unittest

from scripts.bounded_process import OutputLimitExceeded, ProcessTimedOut, run_bounded


class BoundedProcessTests(unittest.TestCase):
    def test_captures_both_streams_within_shared_budget(self) -> None:
        result = run_bounded(
            [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
            input_text="",
            timeout=5,
            max_output_bytes=100,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "out\n")
        self.assertEqual(result.stderr, "err\n")

    def test_terminates_when_combined_output_exceeds_budget(self) -> None:
        with self.assertRaises(OutputLimitExceeded):
            run_bounded(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.stdout.write('a' * 700); sys.stderr.write('b' * 700)",
                ],
                input_text="",
                timeout=5,
                max_output_bytes=1_000,
            )

    def test_terminates_when_timeout_expires(self) -> None:
        with self.assertRaises(ProcessTimedOut):
            run_bounded(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                input_text="",
                timeout=1,
                max_output_bytes=100,
            )


if __name__ == "__main__":
    unittest.main()
