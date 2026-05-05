from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import gymnasium as gym
import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = PROJECT_ROOT / "results" / "artifacts"
METRIC_DIR = PROJECT_ROOT / "results" / "metrics"
DOCS_DIR = PROJECT_ROOT / "docs"


SUCCESS_THRESHOLDS: Dict[str, float] = {
    "CartPole-v1": 475.0,
    "LunarLander-v3": 200.0,
    "MountainCar-v0": -110.0,
    "Blackjack-v1": 0.05,
}


def load_pickle(path: Path, default):
    if not path.exists():
        return default
    with path.open("rb") as f:
        return pickle.load(f)


def save_pickle(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(obj, f)


def final_eval_mean(run: dict, last_n: int = 3) -> float:
    vals = np.array(run.get("eval_returns", []), dtype=float)
    if vals.size == 0:
        return np.nan
    tail = vals[-last_n:] if vals.size >= last_n else vals
    return float(np.mean(tail))


def auc_eval(run: dict) -> float:
    steps = np.array(run.get("eval_steps", []), dtype=float)
    vals = np.array(run.get("eval_returns", []), dtype=float)
    if steps.size < 2 or vals.size < 2:
        return np.nan
    if steps[-1] <= 0:
        return np.nan
    area = np.trapezoid(vals, steps)
    return float(area / steps[-1])


def timesteps_to_threshold(run: dict, threshold: float) -> float:
    if np.isnan(threshold):
        return np.nan
    steps = run.get("eval_steps", [])
    vals = run.get("eval_returns", [])
    for s, v in zip(steps, vals):
        if float(v) >= threshold:
            return float(s)
    return np.nan


def bootstrap_ci_mean(values: Iterable[float], n_boot: int = 5000, seed: int = 42) -> Tuple[float, float]:
    arr = np.array([v for v in values if not np.isnan(v)], dtype=float)
    if arr.size == 0:
        return np.nan, np.nan
    if arr.size == 1:
        val = float(arr[0])
        return val, val
    rng = np.random.default_rng(seed)
    boots = rng.choice(arr, size=(n_boot, arr.size), replace=True).mean(axis=1)
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return float(lo), float(hi)


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if x.size < 2 or y.size < 2:
        return np.nan
    vx = np.var(x, ddof=1)
    vy = np.var(y, ddof=1)
    pooled_denom = ((x.size - 1) * vx + (y.size - 1) * vy) / (x.size + y.size - 2)
    if pooled_denom <= 0:
        diff = float(np.mean(x) - np.mean(y))
        if diff == 0:
            return 0.0
        return float(np.sign(diff) * np.inf)
    pooled_std = float(np.sqrt(pooled_denom))
    return float((np.mean(x) - np.mean(y)) / pooled_std)


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if x.size == 0 or y.size == 0:
        return np.nan
    gt = 0
    lt = 0
    for a in x:
        gt += int(np.sum(a > y))
        lt += int(np.sum(a < y))
    return float((gt - lt) / (x.size * y.size))


def holm_adjust(pvals: List[float]) -> List[float]:
    p = np.array(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    sorted_p = p[order]
    adjusted_sorted = np.empty_like(sorted_p)
    running_max = 0.0
    for i, pv in enumerate(sorted_p):
        adj = (m - i) * pv
        running_max = max(running_max, adj)
        adjusted_sorted[i] = min(1.0, running_max)
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def make_env(env_id: str):
    return gym.make(env_id)


def run_random_baseline(env_id: str, episodes_per_seed: int, seeds: List[int]) -> List[float]:
    values = []
    for seed in seeds:
        env = make_env(env_id)
        ep_returns = []
        for ep in range(episodes_per_seed):
            _obs, _info = env.reset(seed=seed * 10000 + ep)
            done = False
            total = 0.0
            while not done:
                action = env.action_space.sample()
                _obs, reward, terminated, truncated, _info = env.step(action)
                total += float(reward)
                done = bool(terminated or truncated)
            ep_returns.append(total)
        env.close()
        values.append(float(np.mean(ep_returns)))
    return values


def build_seed_level_df(
    default_results: dict,
    human_results: dict,
    llm_results: dict,
    thresholds: Dict[str, float],
) -> pd.DataFrame:
    rows = []
    for condition, data in [
        ("default", default_results),
        ("human", human_results),
        ("llm", llm_results),
    ]:
        for env_id, runs in data.items():
            threshold = thresholds.get(env_id, np.nan)
            for idx, run in enumerate(runs):
                final = final_eval_mean(run)
                auc = auc_eval(run)
                ttt = timesteps_to_threshold(run, threshold)
                rows.append(
                    {
                        "environment": env_id,
                        "condition": condition,
                        "seed": run.get("seed", idx),
                        "final_eval": final,
                        "auc_eval": auc,
                        "timesteps_to_threshold": ttt,
                        "success": 0 if np.isnan(ttt) else 1,
                    }
                )
    return pd.DataFrame(rows)


def summarize(seed_df: pd.DataFrame, random_baseline: dict, thresholds: Dict[str, float], n_boot: int) -> pd.DataFrame:
    rows = []
    envs = sorted(seed_df["environment"].unique().tolist())
    conditions = ["random", "default", "human", "llm"]

    for env_id in envs:
        threshold = thresholds.get(env_id, np.nan)
        for condition in conditions:
            if condition == "random":
                vals = np.array(random_baseline.get(env_id, []), dtype=float)
                n = int(vals.size)
                final_mean = float(np.mean(vals)) if n else np.nan
                final_std = float(np.std(vals, ddof=0)) if n else np.nan
                ci_lo, ci_hi = bootstrap_ci_mean(vals, n_boot=n_boot)
                success_rate = float(np.mean(vals >= threshold)) if n else np.nan
                rows.append(
                    {
                        "environment": env_id,
                        "condition": condition,
                        "n_seeds": n,
                        "final_eval_mean": final_mean,
                        "final_eval_std": final_std,
                        "final_eval_ci_low": ci_lo,
                        "final_eval_ci_high": ci_hi,
                        "auc_mean": np.nan,
                        "auc_std": np.nan,
                        "auc_ci_low": np.nan,
                        "auc_ci_high": np.nan,
                        "sample_efficiency_median_steps": np.nan,
                        "success_rate": success_rate,
                        "threshold": threshold,
                    }
                )
                continue

            sub = seed_df[(seed_df["environment"] == env_id) & (seed_df["condition"] == condition)]
            final_vals = sub["final_eval"].to_numpy(dtype=float)
            auc_vals = sub["auc_eval"].to_numpy(dtype=float)
            ttt_vals = sub["timesteps_to_threshold"].to_numpy(dtype=float)
            success_vals = sub["success"].to_numpy(dtype=float)

            final_ci_lo, final_ci_hi = bootstrap_ci_mean(final_vals, n_boot=n_boot)
            auc_ci_lo, auc_ci_hi = bootstrap_ci_mean(auc_vals, n_boot=n_boot)

            ttt_valid = ttt_vals[~np.isnan(ttt_vals)]
            ttt_median = float(np.median(ttt_valid)) if ttt_valid.size else np.nan

            rows.append(
                {
                    "environment": env_id,
                    "condition": condition,
                    "n_seeds": int(sub.shape[0]),
                    "final_eval_mean": float(np.nanmean(final_vals)) if sub.shape[0] else np.nan,
                    "final_eval_std": float(np.nanstd(final_vals, ddof=0)) if sub.shape[0] else np.nan,
                    "final_eval_ci_low": final_ci_lo,
                    "final_eval_ci_high": final_ci_hi,
                    "auc_mean": float(np.nanmean(auc_vals)) if sub.shape[0] else np.nan,
                    "auc_std": float(np.nanstd(auc_vals, ddof=0)) if sub.shape[0] else np.nan,
                    "auc_ci_low": auc_ci_lo,
                    "auc_ci_high": auc_ci_hi,
                    "sample_efficiency_median_steps": ttt_median,
                    "success_rate": float(np.nanmean(success_vals)) if sub.shape[0] else np.nan,
                    "threshold": threshold,
                }
            )
    return pd.DataFrame(rows)


def pairwise_tests(seed_df: pd.DataFrame, random_baseline: dict, n_boot: int) -> pd.DataFrame:
    rows = []
    pairs = [
        ("llm", "human"),
        ("llm", "default"),
        ("human", "default"),
        ("llm", "random"),
        ("human", "random"),
        ("default", "random"),
    ]
    envs = sorted(seed_df["environment"].unique().tolist())

    for env_id in envs:
        for a, b in pairs:
            if a == "random":
                x = np.array(random_baseline.get(env_id, []), dtype=float)
            else:
                x = seed_df[(seed_df["environment"] == env_id) & (seed_df["condition"] == a)]["final_eval"].to_numpy(dtype=float)
            if b == "random":
                y = np.array(random_baseline.get(env_id, []), dtype=float)
            else:
                y = seed_df[(seed_df["environment"] == env_id) & (seed_df["condition"] == b)]["final_eval"].to_numpy(dtype=float)

            x = x[~np.isnan(x)]
            y = y[~np.isnan(y)]
            if x.size == 0 or y.size == 0:
                p_mwu = np.nan
                stat_mwu = np.nan
                p_t = np.nan
            else:
                try:
                    mwu = stats.mannwhitneyu(x, y, alternative="two-sided")
                    stat_mwu = float(mwu.statistic)
                    p_mwu = float(mwu.pvalue)
                except Exception:
                    stat_mwu = np.nan
                    p_mwu = np.nan
                try:
                    ttest = stats.ttest_ind(x, y, equal_var=False, nan_policy="omit")
                    p_t = float(ttest.pvalue)
                except Exception:
                    p_t = np.nan

            diff = float(np.mean(x) - np.mean(y)) if x.size and y.size else np.nan
            diff_ci_lo, diff_ci_hi = np.nan, np.nan
            if x.size and y.size:
                rng = np.random.default_rng(42)
                bx = rng.choice(x, size=(n_boot, x.size), replace=True).mean(axis=1)
                by = rng.choice(y, size=(n_boot, y.size), replace=True).mean(axis=1)
                bdiff = bx - by
                diff_ci_lo, diff_ci_hi = [float(v) for v in np.quantile(bdiff, [0.025, 0.975])]

            rows.append(
                {
                    "environment": env_id,
                    "condition_a": a,
                    "condition_b": b,
                    "n_a": int(x.size),
                    "n_b": int(y.size),
                    "mean_a": float(np.mean(x)) if x.size else np.nan,
                    "mean_b": float(np.mean(y)) if y.size else np.nan,
                    "mean_diff_a_minus_b": diff,
                    "mean_diff_ci_low": diff_ci_lo,
                    "mean_diff_ci_high": diff_ci_hi,
                    "mannwhitney_u": stat_mwu,
                    "p_mannwhitney": p_mwu,
                    "p_welch_ttest": p_t,
                    "cohens_d": cohens_d(x, y) if x.size and y.size else np.nan,
                    "cliffs_delta": cliffs_delta(x, y) if x.size and y.size else np.nan,
                }
            )

    df = pd.DataFrame(rows)
    valid_mask = ~df["p_mannwhitney"].isna()
    if valid_mask.any():
        adjusted = holm_adjust(df.loc[valid_mask, "p_mannwhitney"].tolist())
        df.loc[valid_mask, "p_mannwhitney_holm"] = adjusted
        df["significant_0_05_holm"] = df["p_mannwhitney_holm"] < 0.05
    else:
        df["p_mannwhitney_holm"] = np.nan
        df["significant_0_05_holm"] = False
    return df


def prompt_variation_stats(variation_results: dict, prompt_env: str, threshold: float, n_boot: int) -> pd.DataFrame:
    rows = []
    for prompt_name, payload in variation_results.items():
        meta = payload.get("meta", {})
        runs = payload.get("runs", [])
        finals = np.array([final_eval_mean(r) for r in runs], dtype=float)
        aucs = np.array([auc_eval(r) for r in runs], dtype=float)
        ttts = np.array([timesteps_to_threshold(r, threshold) for r in runs], dtype=float)
        success = np.array([0 if np.isnan(v) else 1 for v in ttts], dtype=float)
        final_ci_lo, final_ci_hi = bootstrap_ci_mean(finals, n_boot=n_boot)
        auc_ci_lo, auc_ci_hi = bootstrap_ci_mean(aucs, n_boot=n_boot)
        ttt_valid = ttts[~np.isnan(ttts)]
        rows.append(
            {
                "prompt_environment": prompt_env,
                "prompt": prompt_name,
                "generation_status": meta.get("status", "missing"),
                "finish_reason": meta.get("finish_reason", "missing"),
                "detail": meta.get("detail", ""),
                "n_runs": int(len(runs)),
                "final_eval_mean": float(np.nanmean(finals)) if len(runs) else np.nan,
                "final_eval_std": float(np.nanstd(finals, ddof=0)) if len(runs) else np.nan,
                "final_eval_ci_low": final_ci_lo,
                "final_eval_ci_high": final_ci_hi,
                "auc_mean": float(np.nanmean(aucs)) if len(runs) else np.nan,
                "auc_std": float(np.nanstd(aucs, ddof=0)) if len(runs) else np.nan,
                "auc_ci_low": auc_ci_lo,
                "auc_ci_high": auc_ci_hi,
                "sample_efficiency_median_steps": float(np.median(ttt_valid)) if ttt_valid.size else np.nan,
                "success_rate": float(np.nanmean(success)) if len(runs) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def generation_reliability(llm_meta: dict, variation_results: dict) -> pd.DataFrame:
    core_status = [v.get("status", "missing") for v in llm_meta.values()]
    var_status = [v.get("meta", {}).get("status", "missing") for v in variation_results.values()]
    combined = core_status + var_status

    rows = []
    for group_name, statuses in [
        ("core_env_prompts", core_status),
        ("prompt_variation_prompts", var_status),
        ("combined", combined),
    ]:
        total = len(statuses)
        ok = int(sum(s == "ok" for s in statuses))
        rows.append(
            {
                "group": group_name,
                "total_prompts": total,
                "ok_count": ok,
                "ok_rate": (ok / total) if total else np.nan,
                "syntax_runtime_invalid_count": int(sum(s == "syntax_runtime_invalid" for s in statuses)),
                "truncation_incomplete_count": int(sum(s == "truncation_incomplete" for s in statuses)),
            }
        )
    return pd.DataFrame(rows)


def failure_taxonomy_counts(metrics_dir: Path) -> pd.DataFrame:
    path = metrics_dir / "failure_analysis.csv"
    if not path.exists():
        return pd.DataFrame(
            [
                {
                    "auto_failure_label": "missing_failure_analysis_csv",
                    "count": 0,
                    "rate": np.nan,
                }
            ]
        )
    df = pd.read_csv(path)
    if "auto_failure_label" not in df.columns or df.empty:
        return pd.DataFrame(
            [
                {
                    "auto_failure_label": "unavailable",
                    "count": 0,
                    "rate": np.nan,
                }
            ]
        )
    counts = df["auto_failure_label"].value_counts(dropna=False)
    total = int(counts.sum())
    rows = []
    for label, count in counts.items():
        rows.append(
            {
                "auto_failure_label": label,
                "count": int(count),
                "rate": (int(count) / total) if total else np.nan,
            }
        )
    return pd.DataFrame(rows)


def write_report(
    summary_df: pd.DataFrame,
    pairwise_df: pd.DataFrame,
    prompt_df: pd.DataFrame,
    reliability_df: pd.DataFrame,
    failure_counts_df: pd.DataFrame,
    out_path: Path,
) -> None:
    def table_or_note(df: pd.DataFrame, note: str = "No data available.") -> str:
        if df is None or df.empty:
            return note
        return df.to_markdown(index=False)

    lines: List[str] = []
    lines.append("# Research Validation Report")
    lines.append("")
    lines.append("This report computes confidence intervals, effect sizes, and significance tests from saved seed-level artifacts.")
    lines.append("")

    lines.append("## Aggregate Performance (Final Eval Mean)")
    lines.append("")
    for env_id in summary_df["environment"].dropna().unique():
        lines.append(f"### {env_id}")
        sub = summary_df[summary_df["environment"] == env_id].copy()
        cols = [
            "condition",
            "n_seeds",
            "final_eval_mean",
            "final_eval_ci_low",
            "final_eval_ci_high",
            "sample_efficiency_median_steps",
            "success_rate",
        ]
        lines.append(sub[cols].to_markdown(index=False))
        lines.append("")

    lines.append("## Key Pairwise Tests (Mann-Whitney with Holm correction)")
    lines.append("")
    key = pairwise_df[
        pairwise_df["condition_a"].isin(["llm", "human"])
        & pairwise_df["condition_b"].isin(["default", "human"])
    ][
        [
            "environment",
            "condition_a",
            "condition_b",
            "mean_a",
            "mean_b",
            "mean_diff_a_minus_b",
            "p_mannwhitney",
            "p_mannwhitney_holm",
            "significant_0_05_holm",
            "cohens_d",
            "cliffs_delta",
        ]
    ]
    lines.append(key.to_markdown(index=False))
    lines.append("")

    lines.append("## Prompt Variation Reliability")
    lines.append("")
    lines.append(table_or_note(prompt_df))
    lines.append("")

    lines.append("## LLM Generation Reliability")
    lines.append("")
    lines.append(table_or_note(reliability_df))
    lines.append("")

    lines.append("## Failure Taxonomy Counts")
    lines.append("")
    lines.append(table_or_note(failure_counts_df))
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute research-grade statistics from RL reward experiments.")
    parser.add_argument("--episodes-random", type=int, default=200, help="Random baseline episodes per seed (default: 200)")
    parser.add_argument("--bootstrap", type=int, default=5000, help="Bootstrap samples for CIs (default: 5000)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    METRIC_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    default_results = load_pickle(ARTIFACT_DIR / "default_results.pkl", {})
    human_results = load_pickle(ARTIFACT_DIR / "human_results.pkl", {})
    llm_results = load_pickle(ARTIFACT_DIR / "llm_results.pkl", {})
    llm_meta = load_pickle(ARTIFACT_DIR / "llm_meta.pkl", {})
    variation_results_cartpole = load_pickle(ARTIFACT_DIR / "variation_results.pkl", {})
    variation_results_blackjack = load_pickle(ARTIFACT_DIR / "variation_results_blackjack.pkl", {})

    if not default_results or not human_results or not llm_results:
        raise RuntimeError("Missing core artifacts. Expected default/human/llm result pickles in results/artifacts.")

    envs = sorted(default_results.keys())
    seeds = sorted({int(run.get("seed", 0)) for env_runs in default_results.values() for run in env_runs})

    random_path = ARTIFACT_DIR / "random_baseline.pkl"
    random_baseline = load_pickle(random_path, {})
    for env_id in envs:
        existing = random_baseline.get(env_id, [])
        if not isinstance(existing, list) or len(existing) != len(seeds):
            print(f"[random] computing baseline for {env_id} ({args.episodes_random} episodes x {len(seeds)} seeds)")
            random_baseline[env_id] = run_random_baseline(
                env_id=env_id,
                episodes_per_seed=args.episodes_random,
                seeds=seeds,
            )
    save_pickle(random_path, random_baseline)

    seed_df = build_seed_level_df(default_results, human_results, llm_results, SUCCESS_THRESHOLDS)
    summary_df = summarize(seed_df, random_baseline, SUCCESS_THRESHOLDS, n_boot=args.bootstrap)
    pairwise_df = pairwise_tests(seed_df, random_baseline, n_boot=args.bootstrap)
    prompt_frames = []
    if isinstance(variation_results_cartpole, dict) and variation_results_cartpole:
        prompt_frames.append(
            prompt_variation_stats(
                variation_results_cartpole,
                prompt_env="CartPole-v1",
                threshold=SUCCESS_THRESHOLDS.get("CartPole-v1", np.nan),
                n_boot=args.bootstrap,
            )
        )
    if isinstance(variation_results_blackjack, dict) and variation_results_blackjack:
        prompt_frames.append(
            prompt_variation_stats(
                variation_results_blackjack,
                prompt_env="Blackjack-v1",
                threshold=SUCCESS_THRESHOLDS.get("Blackjack-v1", np.nan),
                n_boot=args.bootstrap,
            )
        )
    prompt_df = pd.concat(prompt_frames, ignore_index=True) if prompt_frames else pd.DataFrame()

    variation_for_reliability = {}
    if isinstance(variation_results_cartpole, dict):
        variation_for_reliability.update({f"cartpole::{k}": v for k, v in variation_results_cartpole.items()})
    if isinstance(variation_results_blackjack, dict):
        variation_for_reliability.update({f"blackjack::{k}": v for k, v in variation_results_blackjack.items()})

    reliability_df = generation_reliability(llm_meta, variation_for_reliability)
    failure_counts_df = failure_taxonomy_counts(METRIC_DIR)

    seed_df.to_csv(METRIC_DIR / "research_seed_level_metrics.csv", index=False)
    summary_df.to_csv(METRIC_DIR / "research_summary_with_ci.csv", index=False)
    pairwise_df.to_csv(METRIC_DIR / "research_pairwise_tests.csv", index=False)
    prompt_df.to_csv(METRIC_DIR / "research_prompt_variation_stats.csv", index=False)
    reliability_df.to_csv(METRIC_DIR / "research_generation_reliability.csv", index=False)
    failure_counts_df.to_csv(METRIC_DIR / "research_failure_taxonomy_counts.csv", index=False)

    report_path = DOCS_DIR / "research_validation_report.md"
    write_report(summary_df, pairwise_df, prompt_df, reliability_df, failure_counts_df, report_path)

    print("Saved:")
    print("-", METRIC_DIR / "research_seed_level_metrics.csv")
    print("-", METRIC_DIR / "research_summary_with_ci.csv")
    print("-", METRIC_DIR / "research_pairwise_tests.csv")
    print("-", METRIC_DIR / "research_prompt_variation_stats.csv")
    print("-", METRIC_DIR / "research_generation_reliability.csv")
    print("-", METRIC_DIR / "research_failure_taxonomy_counts.csv")
    print("-", report_path)


if __name__ == "__main__":
    main()
