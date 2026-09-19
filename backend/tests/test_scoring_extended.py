from backend.scoring import score

def test_score_sum():
    # Test that points sum to score before cap
    signals = [
        {"signal_id": "flagged_address", "severity": "high"},
        {"signal_id": "flagged_counterparty", "severity": "high"},
        {"signal_id": "flagged_counterparty", "severity": "high"},
    ]
    res = score(signals)
    pts_sum = sum(p["points"] for p in res["points"])
    # 60 + 45 = 105
    assert pts_sum == 105
    assert res["score"] == 100 # Capped

    signals2 = [
        {"signal_id": "unverified_contract", "severity": "medium"},
    ]
    res2 = score(signals2)
    pts_sum2 = sum(p["points"] for p in res2["points"])
    assert pts_sum2 == 15 # 20 * 0.75
    assert res2["score"] == 15
