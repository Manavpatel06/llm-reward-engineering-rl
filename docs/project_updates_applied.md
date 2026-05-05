# Project Updates Applied

This file maps your voice-note feedback to concrete implementation changes.

## 1) "Do literature review first"
- Added: `literature_review.md`
- Includes prior work summary, gap identification, and project positioning.

## 2) "Establish a good baseline"
- In `Plannin_project_v3.ipynb`:
  - Added/kept `default` and `human` baselines with 5 seeds.
  - Added a `random` baseline (`run_random_baseline`) for floor comparison.
  - Summary table now reports `random`, `default`, `human`, and `llm`.

## 3) "Pick another domain and test behavior there"
- Added new environment: `Blackjack-v1`.
- Added train budget and success threshold for Blackjack.
- Added prompt template and human-shaped reward function for Blackjack.
- Added tuple-observation wrapper to support environments like Blackjack in SB3.

## 4) "Introduce changes systematically"
- Maintained one unified experiment pipeline across all domains.
- Reused the same seeds, PPO setup, and evaluation protocol.
- Kept resumable checkpoints for long runs.

## 5) "Use more human-understandable games than CartPole"
- Added Blackjack as a human-understandable game domain.
- Moved prompt variation experiment to Blackjack (`vague/detailed/hint_based`).

## Main Updated Notebook
- `Plannin_project_v3.ipynb`

## Notes
- `Plannin_project_v2.ipynb` is kept unchanged for reproducibility of previous run outputs.
