#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


REPOSITORY = "https://github.com/Vprogrammers/mobile-a11y-agent-skills"


def source_commit(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
    )
    return completed.stdout.strip()


def build(root: Path, output: Path, commit: str | None = None) -> None:
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError("Output must be outside the canonical repository.")
    if output.exists():
        shutil.rmtree(output)

    claude = output / ".claude"
    claude.mkdir(parents=True)
    shutil.copy2(root / "distribution/light/CLAUDE.md", claude / "CLAUDE.md")
    shutil.copytree(root / "agents", claude / "agents")
    shutil.copytree(root / "skills", claude / "skills")
    shutil.copy2(root / "distribution/light/README.md", output / "README.md")
    shutil.copy2(root / "distribution/light/CONTRIBUTING.md", output / "CONTRIBUTING.md")
    shutil.copy2(root / "LICENSE", output / "LICENSE")

    workflows = output / ".github/workflows"
    workflows.mkdir(parents=True)
    shutil.copy2(root / "distribution/light/sync.yml", workflows / "sync.yml")

    provenance = {
        "generated": True,
        "source_repository": REPOSITORY,
        "source_commit": commit or source_commit(root),
    }
    (output / ".source.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the copy-ready light distribution.")
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    build(Path(__file__).resolve().parent.parent, args.output, args.source_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
