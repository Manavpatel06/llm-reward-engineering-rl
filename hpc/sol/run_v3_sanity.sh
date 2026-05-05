#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_ROOT}"

mkdir -p results/logs ollama_models

export PYTHONUNBUFFERED=1
export OLLAMA_MODELS="${OLLAMA_MODELS:-${PROJECT_ROOT}/ollama_models}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"

echo "PROJECT_ROOT=${PROJECT_ROOT}"
echo "OLLAMA_MODELS=${OLLAMA_MODELS}"
echo "OLLAMA_MODEL=${OLLAMA_MODEL}"
echo "Start time: $(date)"

if command -v ollama-start >/dev/null 2>&1; then
  ollama-start
  trap 'ollama-stop || true' EXIT
fi

if command -v ollama >/dev/null 2>&1; then
  ollama pull "${OLLAMA_MODEL}"
fi

python scripts/run_experiment.py --config configs/experiment_v3_sol_sanity.json

echo "End time: $(date)"
