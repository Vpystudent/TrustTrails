# TrustTrail Evaluation Report

## Setup
Sample size: 2 scam addresses (held-out test set), 2 safe addresses.
List lookups (scam_signal.csv) were DISABLED. This measures the pure predictive power of our rule-based heuristics.

## Results
- **Precision**: 0.00
- **Recall**: 0.00
- **F1 Score**: 0.00

### Confusion Matrix
| | Predicted Bad (Med/High) | Predicted Good (Low) |
|---|---|---|
| **Actual Scam** | 0 (TP) | 2 (FN) |
| **Actual Safe** | 0 (FP) | 2 (TN) |

## Honest Limits
- **Sample Size**: 4 addresses evaluated.
- **EOAs with little history**: Many scam addresses are burn-and-churn wallets. Without the explicit blacklist, they have too little activity to trigger 'risky interaction' or 'unlimited approval' heuristics.
- **List Bias**: The safe addresses are well-known high-profile contracts. They often have upgradeable proxy patterns which trigger our 'upgradeable_proxy' heuristic if not carefully tuned, causing false positives.
