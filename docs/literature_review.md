# Literature Review and Positioning

## Core Prior Work

### EUREKA (2023)
- Introduces an iterative loop where an LLM proposes reward code and receives performance feedback.
- Demonstrates that iterative refinement can discover strong reward functions in complex domains.
- Key takeaway for this project: iterative feedback is powerful, but can hide one-shot reliability issues.

### Text2Reward (2023)
- Focuses on generating reward functions from natural language task descriptions.
- Shows feasibility of mapping language specifications to executable reward code.
- Key takeaway for this project: one-shot text-to-reward is possible, but behavior varies by domain and prompt quality.

## Gap This Project Targets

Existing work already shows that LLMs can generate rewards.  
The remaining gap is systematic reliability analysis under controlled budgets and consistent baselines.

This project's delta:
- One-shot reward generation benchmarked against default and human-shaped baselines.
- Multi-seed comparison with fixed training budgets.
- Cross-domain evaluation including an additional human-understandable game domain (`Blackjack-v1`).
- Explicit failure-mode taxonomy and prompt-quality ablations.

## Updated Research Question

How reliable are one-shot LLM-generated reward functions across multiple RL domains, and what failure patterns appear when compared against strong default, random, and human-shaped baselines?

## Evaluation Dimensions

- Final performance (default-reward evaluation)
- Sample efficiency (timesteps to threshold)
- Robustness (variance across seeds)
- Failure modes (syntax/runtime invalid, truncation, underspecification, reward hacking, magnitude mismatch)
- Prompt sensitivity (vague vs detailed vs hint-based prompts in a human-understandable domain)

## Why the Added Domain Matters

`Blackjack-v1` was added to reduce over-reliance on abstract control tasks and improve interpretability of behavior and reward logic.  
This helps test whether LLM reward design generalizes from physics-style control tasks to decision-oriented, human-understandable gameplay.
