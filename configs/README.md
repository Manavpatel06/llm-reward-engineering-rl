# Configs

JSON configs for reproducible notebook execution through `scripts/run_experiment.py`.

Required keys:
- `project_root`
- `notebook_path`
- `log_path`
- `cells_to_run`

Optional:
- `env`: environment variable overrides for the run.

Notes:
- `project_root` is resolved relative to the config file location.
- `env` values support `${PROJECT_ROOT}` substitution.
- If `project_root` is omitted, runner defaults to the parent of the config directory.
