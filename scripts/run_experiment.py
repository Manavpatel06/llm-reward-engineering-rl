from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import time
import traceback


def _load_config(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def _resolve(root: Path, value: str) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return root / p


def _resolve_project_root(config_path: Path, cfg: dict) -> Path:
    # Resolve project root relative to config location for portability across systems.
    raw = cfg.get("project_root")
    if raw is None:
        return config_path.parent.parent.resolve()

    cfg_dir = config_path.parent.resolve()
    raw_s = str(raw).replace("${CONFIG_DIR}", str(cfg_dir))
    raw_s = os.path.expanduser(os.path.expandvars(raw_s))
    p = Path(raw_s)
    if p.is_absolute():
        return p.resolve()
    return (cfg_dir / p).resolve()


def _expand_value(value: str, project_root: Path) -> str:
    s = str(value).replace("${PROJECT_ROOT}", str(project_root))
    return os.path.expanduser(os.path.expandvars(s))


def run_experiment(config_path: Path) -> None:
    cfg = _load_config(config_path)
    project_root = _resolve_project_root(config_path, cfg)
    notebook_path = _resolve(project_root, cfg["notebook_path"])
    log_path = _resolve(project_root, cfg["log_path"])
    cells_to_run = cfg["cells_to_run"]
    env_overrides = cfg.get("env", {})

    os.environ["PROJECT_ROOT"] = str(project_root)
    for k, v in env_overrides.items():
        os.environ[k] = _expand_value(str(v), project_root)

    os.chdir(project_root)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    ctx = {"__name__": "__main__"}

    with log_path.open("a", encoding="utf-8") as log:
        def w(msg: str) -> None:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{ts}] {msg}"
            print(line)
            log.write(line + "\n")
            log.flush()

        w("=== Notebook run started ===")
        w(f"config={config_path}")
        w(f"cwd={os.getcwd()}")
        w(f"notebook={notebook_path}")
        w(f"OLLAMA_MODELS={os.getenv('OLLAMA_MODELS')}")
        w(f"OLLAMA_MODEL={os.getenv('OLLAMA_MODEL')}")

        for idx in cells_to_run:
            cell = nb["cells"][idx]
            src = cell.get("source", "")
            if isinstance(src, list):
                src = "".join(src)

            w(f"--- Running cell {idx} ---")
            start = time.time()
            try:
                exec(compile(src, f"cell_{idx}", "exec"), ctx)
                dt = time.time() - start
                w(f"--- Cell {idx} completed in {dt / 60:.2f} min ---")
            except Exception as exc:
                w(f"*** Cell {idx} FAILED: {exc}")
                log.write(traceback.format_exc() + "\n")
                log.flush()
                raise

        w("=== Notebook run completed successfully ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run notebook experiment using JSON config.")
    parser.add_argument(
        "--config",
        default="configs/experiment_v3_local.json",
        help="Path to config JSON (default: configs/experiment_v3_local.json)",
    )
    args = parser.parse_args()
    run_experiment(Path(args.config).resolve())


if __name__ == "__main__":
    main()
