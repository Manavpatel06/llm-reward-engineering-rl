#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_ROOT}"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="llm_reward_project_sol_${STAMP}.tar.gz"

tar -czf "${OUT}" \
  --exclude=".git" \
  --exclude="models/*" \
  --exclude="ollama_models/*" \
  --exclude="results/*" \
  --exclude="__pycache__" \
  --exclude="*/__pycache__/*" \
  .

echo "Created ${OUT}"
echo "Upload this tarball to Sol, then extract:"
echo "  tar -xzf ${OUT}"
