# Method Section

Prior work has already shown that LLMs can generate reward code from text (for example, EUREKA and Text2Reward). This project focuses on the remaining gap: a systematic reliability evaluation under fixed budgets and reproducible baselines.

We benchmark across four Gymnasium domains: `CartPole-v1`, `LunarLander-v3`, `MountainCar-v0`, and `Blackjack-v1` (added as a more human-understandable game domain). For each environment, we compare four conditions:

1. Random policy baseline
2. Default environment reward
3. Human-shaped reward
4. One-shot LLM-generated reward

All trainable conditions use PPO (Stable-Baselines3), fixed hyperparameters, and 5 seeds. Budgets are fixed by environment (`100k`, `250k`, `200k`, `150k` steps respectively).

For the LLM condition, reward code is generated one-shot from task descriptions with strict signature/output constraints. Generated code is validated via syntax and runtime checks before training; failures are recorded as LLM-generation failures.

To keep comparisons fair, all trained policies are evaluated under default environment reward (common metric). We report:

1. Final performance (mean ± std over seeds)
2. Sample efficiency (timesteps to threshold)
3. Success rate across seeds
4. Failure-mode label

Failure taxonomy:

- `syntax/runtime invalid`
- `truncation/incomplete output`
- `underspecification`
- `reward hacking/exploit`
- `magnitude mismatch`

Prompt ablation is performed in a human-understandable domain (`Blackjack-v1`) with three prompt styles (`vague`, `detailed`, `hint-based`) using 5 seeds each.

## Table 1. Environment Setup and Success Criteria

| Environment | Role | Train Steps | Success Threshold (Default Eval Return) |
|---|---|---:|---:|
| CartPole-v1 | Dense / easy | 100,000 | 475 |
| LunarLander-v3 | Intermediate | 250,000 | 200 |
| MountainCar-v0 | Sparse / hard | 200,000 | -110 |
| Blackjack-v1 | Human-understandable card game | 150,000 | 0.05 |

## Table 2. Experiment Matrix

| Exp ID | Purpose | Conditions | Environments | Seeds | Primary Outputs |
|---|---|---|---|---:|---|
| E1 | Core benchmark | Random vs Default vs Human vs LLM | All 4 | 5 | Final return, efficiency, success rate |
| E2 | Prompt sensitivity | LLM prompt: vague vs detailed vs hint-based | Blackjack-v1 | 5 | Prompt-quality impact |
| E3 | Failure analysis | All LLM-generated rewards | All applicable | N/A | Taxonomy counts + examples |

## References

[1] EUREKA: https://arxiv.org/abs/2310.12931  
[2] Text2Reward: https://arxiv.org/abs/2309.11489
