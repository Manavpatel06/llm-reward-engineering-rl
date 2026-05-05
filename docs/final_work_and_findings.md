# Can LLMs Engineer Reward Functions?

## Complete Work and Findings (Single-File Report)

Prepared on: **2026-05-02**

## 1) Project Summary

### Title
Can LLMs Engineer Reward Functions? A Systematic Evaluation of LLM-Generated Rewards for RL Agents

### Core Question
Can a large language model generate reward functions from natural language task descriptions, and how do those rewards compare with random, default, and human-shaped rewards in terms of:
- performance,
- sample efficiency,
- reliability,
- failure modes?

### Why this matters
Reward design is one of the hardest and most brittle parts of RL. If LLMs can automate reward engineering reliably, RL development time can drop significantly. If they fail, the failure patterns still provide important scientific insight.

## 2) Positioning Against Prior Work

Existing papers like **EUREKA** and **Text2Reward** already show feasibility of LLM-generated rewards.

This project's delta is a **systematic reliability benchmark** with:
- one-shot reward generation,
- fixed training budgets,
- multi-seed evaluation,
- cross-domain comparison,
- explicit failure-mode taxonomy,
- prompt-ablation study in a human-understandable domain.

## 3) Experimental Setup

### Environments
- `CartPole-v1` (easy dense control)
- `LunarLander-v3` (intermediate control)
- `MountainCar-v0` (sparse-reward hard control)
- `Blackjack-v1` (human-understandable game domain)

### Conditions
- `random`
- `default` environment reward
- `human` shaped reward
- `llm` one-shot generated reward

### Training protocol
- PPO (Stable-Baselines3)
- 5 seeds per condition
- Fixed per-environment timesteps
- Common evaluation metric: **default environment reward**

### Prompt variation study
- Environments: CartPole-v1 and Blackjack-v1
- Prompt styles: `vague`, `detailed`, `hint_based`

## 4) Main Quantitative Results

### 4.1 Core benchmark (means/std/efficiency)

| environment    | condition   |   threshold |   n_seeds |   final_eval_mean |   final_eval_std |   sample_efficiency_median_steps |   success_rate |
|:---------------|:------------|------------:|----------:|------------------:|-----------------:|---------------------------------:|---------------:|
| CartPole-v1    | random      |      475    |         5 |            21.71  |            0.599 |                                  |            0   |
| CartPole-v1    | default     |      475    |         5 |           500     |            0     |                            20000 |            1   |
| CartPole-v1    | human       |      475    |         5 |           500     |            0     |                            20000 |            1   |
| CartPole-v1    | llm         |      475    |         5 |           450.573 |           14.91  |                            70000 |            1   |
| LunarLander-v3 | random      |      200    |         5 |          -187.042 |            8.045 |                                  |            0   |
| LunarLander-v3 | default     |      200    |         5 |           145.089 |           66.192 |                           195000 |            0.6 |
| LunarLander-v3 | human       |      200    |         5 |           -13.063 |           63.013 |                                  |            0   |
| LunarLander-v3 | llm         |      200    |         5 |           104.265 |           40.994 |                                  |            0   |
| MountainCar-v0 | random      |     -110    |         5 |          -200     |            0     |                                  |            0   |
| MountainCar-v0 | default     |     -110    |         5 |          -200     |            0     |                                  |            0   |
| MountainCar-v0 | human       |     -110    |         5 |          -200     |            0     |                                  |            0   |
| MountainCar-v0 | llm         |     -110    |         5 |          -200     |            0     |                                  |            0   |
| Blackjack-v1   | random      |        0.05 |         5 |            -0.399 |            0.057 |                                  |            0   |
| Blackjack-v1   | default     |        0.05 |         5 |            -0.073 |            0.129 |                            10000 |            1   |
| Blackjack-v1   | human       |        0.05 |         5 |            -0.08  |            0.114 |                            15000 |            1   |
| Blackjack-v1   | llm         |        0.05 |         5 |            -0.163 |            0.05  |                            20000 |            1   |

### 4.2 Research summary with confidence intervals

| environment    | condition   |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   auc_mean |   success_rate |
|:---------------|:------------|------------------:|--------------------:|---------------------:|-----------:|---------------:|
| CartPole-v1    | random      |            21.71  |              21.185 |               22.282 |            |            0   |
| CartPole-v1    | default     |           500     |             500     |              500     |    458.018 |            1   |
| CartPole-v1    | human       |           500     |             500     |              500     |    457.378 |            1   |
| CartPole-v1    | llm         |           450.573 |             440.273 |              465.393 |    356.294 |            1   |
| LunarLander-v3 | random      |          -187.042 |            -194.923 |             -180.001 |            |            0   |
| LunarLander-v3 | default     |           145.089 |              88.314 |              201.865 |   -107.328 |            0.6 |
| LunarLander-v3 | human       |           -13.063 |             -65.442 |               42.529 |   -236.509 |            0   |
| LunarLander-v3 | llm         |           104.265 |              68.494 |              140.035 |   -224.036 |            0   |
| MountainCar-v0 | random      |          -200     |            -200     |             -200     |            |            0   |
| MountainCar-v0 | default     |          -200     |            -200     |             -200     |   -195     |            0   |
| MountainCar-v0 | human       |          -200     |            -200     |             -200     |   -195     |            0   |
| MountainCar-v0 | llm         |          -200     |            -200     |             -200     |   -195     |            0   |
| Blackjack-v1   | random      |            -0.399 |              -0.439 |               -0.347 |            |            0   |
| Blackjack-v1   | default     |            -0.073 |              -0.177 |                0.047 |     -0.077 |            1   |
| Blackjack-v1   | human       |            -0.08  |              -0.19  |               -0     |     -0.068 |            1   |
| Blackjack-v1   | llm         |            -0.163 |              -0.203 |               -0.122 |     -0.169 |            1   |

### 4.3 Pairwise comparisons (effect + significance)

(Comparison metric: mean difference = condition_a - condition_b)

| environment    | condition_a   | condition_b   |   mean_diff_a_minus_b |   p_mannwhitney |   p_mannwhitney_holm |   cohens_d |   cliffs_delta |
|:---------------|:--------------|:--------------|----------------------:|----------------:|---------------------:|-----------:|---------------:|
| CartPole-v1    | human         | default       |                 0     |           1     |                1     |      0     |           0    |
| CartPole-v1    | llm           | default       |               -49.427 |           0.007 |                0.18  |     -4.193 |          -1    |
| CartPole-v1    | llm           | human         |               -49.427 |           0.007 |                0.18  |     -4.193 |          -1    |
| LunarLander-v3 | human         | default       |              -158.152 |           0.008 |                0.18  |     -2.189 |          -1    |
| LunarLander-v3 | llm           | default       |               -40.825 |           0.421 |                1     |     -0.663 |          -0.36 |
| LunarLander-v3 | llm           | human         |               117.328 |           0.032 |                0.381 |      1.974 |           0.84 |
| MountainCar-v0 | human         | default       |                 0     |           1     |                1     |      0     |           0    |
| MountainCar-v0 | llm           | default       |                 0     |           1     |                1     |      0     |           0    |
| MountainCar-v0 | llm           | human         |                 0     |           1     |                1     |      0     |           0    |
| Blackjack-v1   | human         | default       |                -0.007 |           0.6   |                1     |     -0.049 |           0.24 |
| Blackjack-v1   | llm           | default       |                -0.09  |           0.31  |                1     |     -0.823 |          -0.44 |
| Blackjack-v1   | llm           | human         |                -0.083 |           0.151 |                1     |     -0.846 |          -0.6  |

## 5) Reliability and Failure Modes

### 5.1 LLM generation reliability

| group                    |   total_prompts |   ok_count |   ok_rate |   syntax_runtime_invalid_count |   truncation_incomplete_count |
|:-------------------------|----------------:|-----------:|----------:|-------------------------------:|------------------------------:|
| core_env_prompts         |               4 |          4 |       1   |                              0 |                             0 |
| prompt_variation_prompts |               6 |          3 |       0.5 |                              3 |                             0 |
| combined                 |              10 |          7 |       0.7 |                              3 |                             0 |

### 5.2 Failure taxonomy counts

| auto_failure_label   |   count |   rate |
|:---------------------|--------:|-------:|
| reward_hacking       |       2 |   0.5  |
| magnitude_mismatch   |       1 |   0.25 |
| underspecification   |       1 |   0.25 |

### 5.3 Environment-level failure labels

| environment    | auto_failure_label   | generation_status   | detail         |
|:---------------|:---------------------|:--------------------|:---------------|
| CartPole-v1    | magnitude_mismatch   | ok                  | valid function |
| LunarLander-v3 | underspecification   | ok                  | valid function |
| MountainCar-v0 | reward_hacking       | ok                  | valid function |
| Blackjack-v1   | reward_hacking       | ok                  | valid function |

## 6) Prompt Variation Findings

| prompt_environment   | prompt     | generation_status      |   n_runs |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   sample_efficiency_median_steps |   success_rate | detail                                                                                                                                     |
|:---------------------|:-----------|:-----------------------|---------:|------------------:|--------------------:|---------------------:|---------------------------------:|---------------:|:-------------------------------------------------------------------------------------------------------------------------------------------|
| CartPole-v1          | detailed   | syntax_runtime_invalid |        0 |                   |                     |                      |                                  |                | Runtime test failed: name 'np' is not defined                                                                                              |
| CartPole-v1          | hint_based | ok                     |        5 |           500     |             500     |              500     |                            15000 |              1 | valid function                                                                                                                             |
| CartPole-v1          | vague      | syntax_runtime_invalid |        0 |                   |                     |                      |                                  |                | Runtime test failed: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices |
| Blackjack-v1         | detailed   | ok                     |        5 |            -0.08  |              -0.167 |                0.007 |                            20000 |              1 | valid function                                                                                                                             |
| Blackjack-v1         | hint_based | ok                     |        5 |             0.047 |              -0.083 |                0.177 |                            25000 |              1 | valid function                                                                                                                             |
| Blackjack-v1         | vague      | syntax_runtime_invalid |        0 |                   |                     |                      |                                  |                | Runtime test failed: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices |

## 7) Interpreted Findings

1. **CartPole-v1**
- Default and human rewards saturated at the max return (`500.0`).
- LLM reward remained lower (`450.573`) and needed more timesteps to threshold, indicating poorer sample efficiency and likely reward-scale/mismatch issues.

2. **LunarLander-v3**
- Default reward performed best (`145.089`).
- LLM (`104.265`) outperformed human-shaped reward (`-13.063`) but did not reach default-level success.

3. **MountainCar-v0**
- All methods collapsed to the same poor return (`-200`), showing a domain where current shaping/generation setup was insufficient.

4. **Blackjack-v1**
- Default (`-0.073`) and human (`-0.080`) were better than LLM (`-0.163`) on final mean return.
- Prompt quality mattered: `hint_based` produced stronger behavior than `detailed`, while `vague` often failed code validation.

5. **Reliability insight**
- Core prompts were reliable (100% valid generation), but prompt-variation validity dropped (50%), confirming that specification quality strongly affects one-shot reward generation.

6. **Statistical note**
- Several uncorrected p-values were low, but Holm-corrected significance was not reached in these key LLM-vs-baseline tests (limited power at n=5 seeds).

## 8) Contributions Claimed by This Project

- A reproducible one-shot LLM reward benchmark across 4 domains.
- Unified comparison against random/default/human baselines.
- Seeded evaluation with sample-efficiency and success metrics.
- Failure-mode taxonomy with quantified counts.
- Prompt-ablation evidence in a human-understandable domain.

## 9) Limitations

- Seed count (5) limits statistical power.
- Single primary local LLM family in final runs.
- Fixed PPO hyperparameters may underfit some domains (notably MountainCar).
- One-shot generation only (no iterative refinement loop like EUREKA).

## 10) Reproducibility Artifacts

- Main notebook: `notebooks/Plannin_project_v3.ipynb`
- Runner: `scripts/run_experiment.py`
- Research stats: `scripts/research_eval.py`
- Core outputs:
  - `results/metrics/summary_metrics.csv`
  - `results/metrics/failure_analysis.csv`
  - `results/metrics/research_summary_with_ci.csv`
  - `results/metrics/research_pairwise_tests.csv`
  - `results/metrics/research_prompt_variation_stats.csv`
  - `results/metrics/research_generation_reliability.csv`
  - `results/figures/eval_curve_*.png`

## 11) Final Conclusion

LLMs can produce executable reward functions and sometimes competitive performance, but one-shot reliability is domain- and prompt-sensitive. In this benchmark, LLM rewards were clearly useful yet inconsistent versus strong handcrafted/default baselines. The most defensible conclusion is not that LLM reward design is solved, but that it is promising and requires stronger prompt protocols, better validation gates, and broader statistical evaluation before trusted deployment.
