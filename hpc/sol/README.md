# Run On ASU Sol (Direct Upload + Submit)

This folder is prepared so you can upload the project to Sol and run it with Slurm.

## 1. Upload

From your local machine, upload this whole project folder to Sol (for example into `/scratch/<asurite>/Project`), then SSH:

```bash
ssh <asurite>@sol.asu.edu
cd /scratch/<asurite>/Project
```

## 2. Build Python Environment (one-time)

Use a short interactive compute session (recommended by ASU RC docs for package installs):

```bash
interactive -p htc -q public -t 30 -c 4
module purge
module load mamba/latest
bash hpc/sol/setup_env.sh rl_reward_sol
exit
```

## 3. Run a Quick Sanity Job

This validates environment + Ollama connectivity + prompt setup:

```bash
sbatch hpc/sol/submit_v3_sanity.sbatch
```

Monitor:

```bash
myjobs
squeue -u $USER
```

## 4. Run Full Project

```bash
sbatch hpc/sol/submit_v3_full.sbatch
```

This runs:
- v3 experiment notebook pipeline via `configs/experiment_v3_sol.json`
- research evaluation statistics via `scripts/research_eval.py`

## 5. Outputs

Results are written inside the uploaded project folder:
- `results/artifacts/`
- `results/metrics/`
- `results/figures/`
- `results/logs/`
- `models/`

Main logs:
- `results/logs/run_v3_sol.log`
- `results/logs/llmreward-v3-full_<jobid>.out`
- `results/logs/llmreward-v3-full_<jobid>.err`

## 6. Optional: Stats-Only Rerun

If training is done and you only want refreshed tables/reports:

```bash
sbatch hpc/sol/submit_research_eval.sbatch
```

## 7. Notes For Account / Email

If your Sol account requires explicit Slurm account selection, edit:
- `hpc/sol/submit_v3_sanity.sbatch`
- `hpc/sol/submit_v3_full.sbatch`
- `hpc/sol/submit_research_eval.sbatch`

Uncomment and set:

```bash
#SBATCH -A grp_<your_group_or_class_account>
```

Optional email notifications are already provided as commented lines.

## 8. Optional: Create a Lightweight Upload Tarball

From local project root:

```bash
bash hpc/sol/make_upload_bundle.sh
```

This excludes heavy local outputs (`models/`, `ollama_models/`, `results/`) so upload is faster.
