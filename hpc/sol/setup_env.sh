#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${1:-rl_reward_sol}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

cd "${PROJECT_ROOT}"

module purge
module load mamba/latest

if mamba env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "Environment ${ENV_NAME} already exists. Skipping creation."
else
  echo "Creating environment ${ENV_NAME} from hpc/sol/environment.yml ..."
  mamba env create -n "${ENV_NAME}" -f hpc/sol/environment.yml
fi

source activate "${ENV_NAME}"
python -V
python - <<'PY'
import gymnasium as gym
import stable_baselines3 as sb3
import numpy as np
import pandas as pd
import matplotlib
import scipy
print("Gymnasium:", gym.__version__)
print("Stable Baselines3:", sb3.__version__)
print("numpy:", np.__version__)
print("pandas:", pd.__version__)
print("matplotlib:", matplotlib.__version__)
print("scipy:", scipy.__version__)
PY

echo "Environment ready: ${ENV_NAME}"
