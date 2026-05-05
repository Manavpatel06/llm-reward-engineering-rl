# LLM Reward Engineering for RL

Systematic evaluation of LLM-generated reward functions vs random, default, and human-shaped rewards for RL agents.

## Research Project Structure

```
Project/
  configs/               # reproducible run configs (JSON)
  data/
    raw/                 # unmodified inputs
    interim/             # intermediate transformed data
    processed/           # final analysis-ready data
  docs/                  # literature review, method, update notes
  notebooks/             # experiment notebooks (v1, v2, v3)
  scripts/               # runnable experiment entrypoints
  src/reward_eval/       # reusable Python package space
  results/
    artifacts/           # .pkl run artifacts
    metrics/             # .csv summaries
    figures/             # plots
    logs/                # execution logs
  reports/               # paper/report drafts
  references/            # external notes/bib/materials
  models/                # trained SB3 checkpoints
  ollama_models/         # local Ollama model store
```

## Main Experiment Notebook

- `notebooks/Plannin_project_v3.ipynb`

## Run Commands

Run v3 with config-driven runner:

```powershell
python scripts/run_experiment.py --config configs/experiment_v3_local.json
```

Quick sanity check (setup + Ollama health + prompts only):

```powershell
python scripts/run_experiment.py --config configs/experiment_v3_sanity.json
```

Run v2 quick wrapper:

```powershell
python scripts/run_v2_local.py
```

Run v3 quick wrapper:

```powershell
python scripts/run_v3_local.py
```

Compute research-grade stats from saved artifacts:

```powershell
python scripts/research_eval.py --episodes-random 200 --bootstrap 5000
```

## ASU Sol HPC Run

SOL-ready Slurm scripts are in `hpc/sol/`.

- Full guide: `hpc/sol/README.md`
- One-time env setup: `hpc/sol/setup_env.sh`
- Sanity submit: `hpc/sol/submit_v3_sanity.sbatch`
- Full submit: `hpc/sol/submit_v3_full.sbatch`
- Stats-only submit: `hpc/sol/submit_research_eval.sbatch`

## Key Outputs

- `results/metrics/summary_metrics.csv`
- `results/metrics/failure_analysis.csv`
- `results/metrics/prompt_variation_summary.csv` (v2) or `prompt_variation_blackjack_summary.csv` (v3)
- `results/metrics/smoke_test_report_v3.json` (smoke test status)
- `results/metrics/research_summary_with_ci.csv` (CIs and aggregate stats)
- `results/metrics/research_pairwise_tests.csv` (effect sizes + significance tests)
- `results/metrics/research_generation_reliability.csv`
- `results/metrics/research_failure_taxonomy_counts.csv`
- `docs/research_validation_report.md`
- `results/figures/*.png`
- `results/artifacts/*.pkl`

## Notes

- `v2` results are preserved.
- `v3` includes the added human-understandable domain (`Blackjack-v1`) and expanded baselines.
