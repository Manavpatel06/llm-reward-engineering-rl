#!/bin/bash
#SBATCH -J llmreward-v3-full
#SBATCH -N 1
#SBATCH -c 16
#SBATCH -t 0-04:00:00
#SBATCH -p htc
#SBATCH -q public
#SBATCH -G 1
#SBATCH --output=results/logs/%x_%j.out
#SBATCH --error=results/logs/%x_%j.err
#SBATCH --export=NONE
## Optional if you need explicit account selection:
##SBATCH -A grp_<your_group_or_class_account>
## Optional mail notifications:
##SBATCH --mail-type=END,FAIL
##SBATCH --mail-user=<asurite>@asu.edu

set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"

module purge
module load mamba/latest
module load ollama/0.3.12 || module load ollama/latest

source activate rl_reward_sol

bash hpc/sol/run_v3_full.sh
