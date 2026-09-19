def score(signals):
    weights = {
        "flagged_counterparty": 40,
        "flagged_contract": 40,
        "flagged_address": 60,
        "unlimited_approval": 35,
        "unverified_contract": 20,
        "nft_approval_for_all": 20,
        "upgradeable_proxy": 15,
        "fresh_wallet_pattern": 15,
        "risky_contract_interaction": 15,
        "new_contract": 10,
        "risky_functions": 10,
        "owner_privileges": 10
    }
    
    severity_multiplier = {
        "low": 0.5,
        "medium": 0.75,
        "high": 1.0
    }
    
    signal_counts = {}
    signal_severity = {}
    
    for s in signals:
        sid = s["signal_id"]
        sev = s["severity"]
        signal_counts[sid] = signal_counts.get(sid, 0) + 1
        current_sev = signal_severity.get(sid, "low")
        if severity_multiplier[sev] > severity_multiplier[current_sev]:
            signal_severity[sid] = sev
            
    total_score = 0
    points = []
    
    for sid, count in signal_counts.items():
        base_weight = weights.get(sid, 0)
        sev = signal_severity.get(sid, "medium")
        mult = severity_multiplier.get(sev, 0.75)
        
        extra = min(10, (count - 1) * 5)
        
        pts = (base_weight + extra) * mult
        total_score += pts
        
        points.append({
            "signal_id": sid,
            "points": pts,
            "reason": f"Fired {count} time(s) with max severity {sev}."
        })
        
    capped_score = min(100, int(round(total_score)))
    
    if capped_score < 30:
        overall_risk = "low"
    elif capped_score < 60:
        overall_risk = "medium"
    else:
        overall_risk = "high"
        
    return {
        "overall_risk": overall_risk,
        "score": capped_score,
        "points": points
    }
