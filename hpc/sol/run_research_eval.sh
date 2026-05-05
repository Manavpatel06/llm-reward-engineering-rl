#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_ROOT}"

mkdir -p results/metrics docs

export PYTHONUNBUFFERED=1

python scripts/research_eval.py --episodes-random 200 --bootstrap 5000
