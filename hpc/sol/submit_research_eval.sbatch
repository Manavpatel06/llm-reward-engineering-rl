#!/bin/bash
#SBATCH -J llmreward-stats
#SBATCH -N 1
#SBATCH -c 4
#SBATCH -t 0-00:30:00
#SBATCH -p public
#SBATCH -q public
#SBATCH --output=results/logs/%x_%j.out
#SBATCH --error=results/logs/%x_%j.err
#SBATCH --export=NONE
## Optional if you need explicit account selection:
##SBATCH -A grp_<your_group_or_class_account>

set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"

module purge
module load mamba/latest

source activate rl_reward_sol

bash hpc/sol/run_research_eval.sh
