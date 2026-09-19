import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.scoring import score

def test_scoring_math():
    signals = [
        {"signal_id": "flagged_counterparty", "severity": "high"},
        {"signal_id": "unlimited_approval", "severity": "medium"},
        {"signal_id": "unlimited_approval", "severity": "high"}
    ]
    # flagged_counterparty: base 40, extra 0, mult 1.0 -> 40
    # unlimited_approval: max sev high. base 35, count 2 -> extra 5, mult 1.0 -> 40
    # total: 80 -> high risk
    res = score(signals)
    assert res['score'] == 80
    assert res['overall_risk'] == 'high'
    
    unlimited_pt = next(p for p in res['points'] if p['signal_id'] == 'unlimited_approval')
    assert unlimited_pt['points'] == 40
    
def test_scoring_cap():
    signals = [{"signal_id": "flagged_counterparty", "severity": "high"} for _ in range(100)]
    res = score(signals)
    assert res['score'] == 50 # 40 + min(10, 99*5) = 50 * 1.0 = 50
    assert res['overall_risk'] == 'medium'
