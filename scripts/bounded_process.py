from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
import subprocess
import threading
import time


class OutputLimitExceeded(Exception):
    """Raised after a subprocess is terminated for exceeding its output budget."""


class ProcessTimedOut(Exception):
    """Raised after a subprocess is terminated for exceeding its time budget."""


@dataclass(frozen=True)
class BoundedResult:
    returncode: int
    stdout: str
    stderr: str


def run_bounded(
    command: list[str],
    input_text: str,
    timeout: int,
    max_output_bytes: int,
    poll_interval: float = 0.02,
) -> BoundedResult:
    """Run a command with a shared byte budget for stdout and stderr."""
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    chunks: Queue[tuple[str, bytes | None]] = Queue(maxsize=4)

    def read_stream(name: str, stream) -> None:
        try:
            while chunk := stream.read(64 * 1024):
                chunks.put((name, chunk))
        finally:
            stream.close()
            chunks.put((name, None))

    def write_input() -> None:
        assert process.stdin is not None
        try:
            process.stdin.write(input_text.encode("utf-8"))
        except (BrokenPipeError, OSError):
            pass
        finally:
            process.stdin.close()

    assert process.stdout is not None
    assert process.stderr is not None
    readers = [
        threading.Thread(target=read_stream, args=("stdout", process.stdout), daemon=True),
        threading.Thread(target=read_stream, args=("stderr", process.stderr), daemon=True),
    ]
    for reader in readers:
        reader.start()
    writer = threading.Thread(target=write_input, daemon=True)
    writer.start()

    output = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout
    finished_streams = 0
    failure: type[Exception] | None = None
    while finished_streams < len(readers):
        remaining = deadline - time.monotonic()
        if remaining <= 0 and failure is None:
            failure = ProcessTimedOut
            process.kill()
        try:
            name, chunk = chunks.get(timeout=poll_interval if failure else min(poll_interval, max(remaining, 0.001)))
        except Empty:
            continue
        if chunk is None:
            finished_streams += 1
            continue
        if failure is not None:
            continue
        captured_bytes = len(output["stdout"]) + len(output["stderr"])
        if captured_bytes + len(chunk) > max_output_bytes:
            failure = OutputLimitExceeded
            process.kill()
            continue
        output[name].extend(chunk)

    process.wait()
    writer.join(timeout=1)
    for reader in readers:
        reader.join(timeout=1)
    if failure is not None:
        raise failure
    return BoundedResult(
        returncode=process.returncode,
        stdout=output["stdout"].decode("utf-8", errors="replace"),
        stderr=output["stderr"].decode("utf-8", errors="replace"),
    )
