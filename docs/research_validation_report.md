# Research Validation Report

This report computes confidence intervals, effect sizes, and significance tests from saved seed-level artifacts.

## Aggregate Performance (Final Eval Mean)

### Blackjack-v1
| condition   |   n_seeds |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   sample_efficiency_median_steps |   success_rate |
|:------------|----------:|------------------:|--------------------:|---------------------:|---------------------------------:|---------------:|
| random      |         5 |        -0.399     |           -0.439    |         -0.347       |                              nan |              0 |
| default     |         5 |        -0.0733333 |           -0.176667 |          0.0468333   |                            10000 |              1 |
| human       |         5 |        -0.08      |           -0.19     |         -1.38778e-18 |                            15000 |              1 |
| llm         |         5 |        -0.163333  |           -0.203333 |         -0.121583    |                            20000 |              1 |

### CartPole-v1
| condition   |   n_seeds |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   sample_efficiency_median_steps |   success_rate |
|:------------|----------:|------------------:|--------------------:|---------------------:|---------------------------------:|---------------:|
| random      |         5 |            21.71  |              21.185 |              22.2825 |                              nan |              0 |
| default     |         5 |           500     |             500     |             500      |                            20000 |              1 |
| human       |         5 |           500     |             500     |             500      |                            20000 |              1 |
| llm         |         5 |           450.573 |             440.273 |             465.393  |                            70000 |              1 |

### LunarLander-v3
| condition   |   n_seeds |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   sample_efficiency_median_steps |   success_rate |
|:------------|----------:|------------------:|--------------------:|---------------------:|---------------------------------:|---------------:|
| random      |         5 |          -187.042 |           -194.923  |            -180.001  |                              nan |            0   |
| default     |         5 |           145.089 |             88.3142 |             201.865  |                           195000 |            0.6 |
| human       |         5 |           -13.063 |            -65.442  |              42.5288 |                              nan |            0   |
| llm         |         5 |           104.265 |             68.4937 |             140.035  |                              nan |            0   |

### MountainCar-v0
| condition   |   n_seeds |   final_eval_mean |   final_eval_ci_low |   final_eval_ci_high |   sample_efficiency_median_steps |   success_rate |
|:------------|----------:|------------------:|--------------------:|---------------------:|---------------------------------:|---------------:|
| random      |         5 |              -200 |                -200 |                 -200 |                              nan |              0 |
| default     |         5 |              -200 |                -200 |                 -200 |                              nan |              0 |
| human       |         5 |              -200 |                -200 |                 -200 |                              nan |              0 |
| llm         |         5 |              -200 |                -200 |                 -200 |                              nan |              0 |

## Key Pairwise Tests (Mann-Whitney with Holm correction)

| environment    | condition_a   | condition_b   |      mean_a |       mean_b |   mean_diff_a_minus_b |   p_mannwhitney |   p_mannwhitney_holm | significant_0_05_holm   |   cohens_d |   cliffs_delta |
|:---------------|:--------------|:--------------|------------:|-------------:|----------------------:|----------------:|---------------------:|:------------------------|-----------:|---------------:|
| Blackjack-v1   | llm           | human         |   -0.163333 |   -0.08      |           -0.0833333  |      0.150794   |             1        | False                   | -0.845759  |          -0.6  |
| Blackjack-v1   | llm           | default       |   -0.163333 |   -0.0733333 |           -0.09       |      0.309524   |             1        | False                   | -0.823492  |          -0.44 |
| Blackjack-v1   | human         | default       |   -0.08     |   -0.0733333 |           -0.00666667 |      0.600402   |             1        | False                   | -0.0489592 |           0.24 |
| CartPole-v1    | llm           | human         |  450.573    |  500         |          -49.4267     |      0.00749496 |             0.179879 | False                   | -4.19329   |          -1    |
| CartPole-v1    | llm           | default       |  450.573    |  500         |          -49.4267     |      0.00749496 |             0.179879 | False                   | -4.19329   |          -1    |
| CartPole-v1    | human         | default       |  500        |  500         |            0          |      1          |             1        | False                   |  0         |           0    |
| LunarLander-v3 | llm           | human         |  104.265    |  -13.063     |          117.328      |      0.031746   |             0.380952 | False                   |  1.97419   |           0.84 |
| LunarLander-v3 | llm           | default       |  104.265    |  145.089     |          -40.8249     |      0.420635   |             1        | False                   | -0.663251  |          -0.36 |
| LunarLander-v3 | human         | default       |  -13.063    |  145.089     |         -158.152      |      0.00793651 |             0.179879 | False                   | -2.18896   |          -1    |
| MountainCar-v0 | llm           | human         | -200        | -200         |            0          |      1          |             1        | False                   |  0         |           0    |
| MountainCar-v0 | llm           | default       | -200        | -200         |            0          |      1          |             1        | False                   |  0         |           0    |
| MountainCar-v0 | human         | default       | -200        | -200         |            0          |      1          |             1        | False                   |  0         |           0    |

## Prompt Variation Reliability

| prompt_environment   | prompt     | generation_status      | finish_reason   | detail                                                                                                                                     |   n_runs |   final_eval_mean |   final_eval_std |   final_eval_ci_low |   final_eval_ci_high |    auc_mean |     auc_std |   auc_ci_low |   auc_ci_high |   sample_efficiency_median_steps |   success_rate |
|:---------------------|:-----------|:-----------------------|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------|---------:|------------------:|-----------------:|--------------------:|---------------------:|------------:|------------:|-------------:|--------------:|---------------------------------:|---------------:|
| CartPole-v1          | vague      | syntax_runtime_invalid | UNKNOWN         | Runtime test failed: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices |        0 |       nan         |       nan        |         nan         |         nan          | nan         | nan         |   nan        |   nan         |                              nan |            nan |
| CartPole-v1          | detailed   | syntax_runtime_invalid | UNKNOWN         | Runtime test failed: name 'np' is not defined                                                                                              |        0 |       nan         |       nan        |         nan         |         nan          | nan         | nan         |   nan        |   nan         |                              nan |            nan |
| CartPole-v1          | hint_based | ok                     | STOP            | valid function                                                                                                                             |        5 |       500         |         0        |         500         |         500          | 456.189     |   3.92054   |   452.209    |   458.89      |                            15000 |              1 |
| Blackjack-v1         | vague      | syntax_runtime_invalid | UNKNOWN         | Runtime test failed: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices |        0 |       nan         |       nan        |         nan         |         nan          | nan         | nan         |   nan        |   nan         |                              nan |            nan |
| Blackjack-v1         | detailed   | ok                     | STOP            | valid function                                                                                                                             |        5 |        -0.08      |         0.105093 |          -0.166667  |           0.00666667 |  -0.0998333 |   0.0345382 |    -0.127167 |    -0.0695    |                            20000 |              1 |
| Blackjack-v1         | hint_based | ok                     | STOP            | valid function                                                                                                                             |        5 |         0.0466667 |         0.146591 |          -0.0833333 |           0.176667   |  -0.0475    |   0.0376276 |    -0.077175 |    -0.0114292 |                            25000 |              1 |

## LLM Generation Reliability

| group                    |   total_prompts |   ok_count |   ok_rate |   syntax_runtime_invalid_count |   truncation_incomplete_count |
|:-------------------------|----------------:|-----------:|----------:|-------------------------------:|------------------------------:|
| core_env_prompts         |               4 |          4 |       1   |                              0 |                             0 |
| prompt_variation_prompts |               6 |          3 |       0.5 |                              3 |                             0 |
| combined                 |              10 |          7 |       0.7 |                              3 |                             0 |

## Failure Taxonomy Counts

| auto_failure_label   |   count |   rate |
|:---------------------|--------:|-------:|
| reward_hacking       |       2 |   0.5  |
| magnitude_mismatch   |       1 |   0.25 |
| underspecification   |       1 |   0.25 |
