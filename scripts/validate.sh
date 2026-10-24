#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
python3 scripts/validate_repo.py "$repo_root"
python3 -m py_compile scripts/*.py
python3 scripts/install_smoke.py "$repo_root"
light_distribution="$(mktemp -d)"
trap 'rm -rf "$light_distribution"' EXIT
python3 scripts/build_light_distribution.py "$light_distribution/package"
python3 scripts/validate_light_distribution.py "$light_distribution/package"
python3 -m unittest discover -s tests
