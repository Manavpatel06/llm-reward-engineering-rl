from pathlib import Path
from run_experiment import run_experiment


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    run_experiment(project_root / "configs" / "experiment_v2_local.json")
