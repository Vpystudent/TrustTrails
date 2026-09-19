import os
import csv
import json
import argparse
import sys
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.analyze import analyze

def load_csv(path):
    addrs = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addrs.append(row['address'].lower())
    return addrs

def evaluate(limit=40):
    labels_dir = os.path.join(os.path.dirname(__file__), '..', 'labels')
    scam_test = load_csv(os.path.join(labels_dir, 'scam_test.csv'))
    safe_addrs = load_csv(os.path.join(labels_dir, 'safe_addresses.csv'))
    
    import random
    random.seed(42)
    random.shuffle(scam_test)
    random.shuffle(safe_addrs)
    
    sample_scam = scam_test[:limit]
    sample_safe = safe_addrs[:limit]
    
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    false_positives = []
    false_negatives = []
    
    with patch('backend.analyze.load_scam_list', return_value=set()):
        with patch('backend.wallet_signals.load_scam_list', return_value=set()):
            with patch('backend.contract_signals.load_scam_list', return_value=set()):
                for addr in sample_scam:
                    try:
                        print(f"Eval Scam: {addr}")
                        rep = analyze(addr, ['ethereum'], use_summary=False)
                        if rep['overall_risk'] in ('medium', 'high'):
                            tp += 1
                        else:
                            fn += 1
                            false_negatives.append({"address": addr, "cause": "No heuristics triggered"})
                    except Exception as e:
                        print(f"Error {addr}: {e}")
                        
                for addr in sample_safe:
                    try:
                        print(f"Eval Safe: {addr}")
                        rep = analyze(addr, ['ethereum'], use_summary=False)
                        if rep['overall_risk'] in ('medium', 'high'):
                            fp += 1
                            false_positives.append({"address": addr, "cause": f"Heuristics triggered: {[s['signal_id'] for s in rep['signals']]}"})
                        else:
                            tn += 1
                    except Exception as e:
                        print(f"Error {addr}: {e}")
                        
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    results = {
        "limit": limit,
        "sample_size": len(sample_scam) + len(sample_safe),
        "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
        "metrics": {"precision": precision, "recall": recall, "f1": f1},
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }
    
    eval_dir = os.path.dirname(__file__)
    with open(os.path.join(eval_dir, 'eval_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
        
    md = f"""# TrustTrail Evaluation Report

## Setup
Sample size: {len(sample_scam)} scam addresses (held-out test set), {len(sample_safe)} safe addresses.
List lookups (scam_signal.csv) were DISABLED. This measures the pure predictive power of our rule-based heuristics.

## Results
- **Precision**: {precision:.2f}
- **Recall**: {recall:.2f}
- **F1 Score**: {f1:.2f}

### Confusion Matrix
| | Predicted Bad (Med/High) | Predicted Good (Low) |
|---|---|---|
| **Actual Scam** | {tp} (TP) | {fn} (FN) |
| **Actual Safe** | {fp} (FP) | {tn} (TN) |

## Honest Limits
- **Sample Size**: {results['sample_size']} addresses evaluated.
- **EOAs with little history**: Many scam addresses are burn-and-churn wallets. Without the explicit blacklist, they have too little activity to trigger 'risky interaction' or 'unlimited approval' heuristics.
- **List Bias**: The safe addresses are well-known high-profile contracts. They often have upgradeable proxy patterns which trigger our 'upgradeable_proxy' heuristic if not carefully tuned, causing false positives.
"""
    with open(os.path.join(eval_dir, 'eval_report.md'), 'w') as f:
        f.write(md)
        
    print(f"Eval done. Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=40)
    args = parser.parse_args()
    evaluate(args.limit)
