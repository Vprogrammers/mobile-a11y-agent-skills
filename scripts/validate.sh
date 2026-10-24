#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo_root/scripts/validate_repo.py" "$repo_root"
python3 -m py_compile "$repo_root"/scripts/*.py
python3 "$repo_root/scripts/install_smoke.py" "$repo_root"
(cd "$repo_root" && python3 -m unittest discover -s tests)
