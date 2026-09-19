import time
import json
import os
from datetime import datetime, timezone
from backend.chains import is_contract
from backend.wallet_signals import run as run_wallet_signals, load_scam_list
from backend.contract_signals import check_contract
from backend.scoring import score
from backend.summary import write_summary

def validate_address(address: str) -> bool:
    if not address or not isinstance(address, str): return False
    return address.startswith('0x') and len(address) == 42 and all(c in '0123456789abcdefABCDEFx' for c in address)

def analyze(address: str, chain_ids: list, use_summary=True):
    address = address.lower()
    if not validate_address(address):
        raise ValueError("Invalid address format")
        
    start_time = datetime.now(timezone.utc).isoformat()
    
    findings = []
    warnings = []
    
    is_addr_contract = False
    
    scam_list = load_scam_list()
    
    for cid in chain_ids:
        try:
            is_c = is_contract(address, cid)
            if is_c:
                is_addr_contract = True
                f = check_contract(address, cid)
                findings.extend(f)
            else:
                f = run_wallet_signals(address, cid)
                findings.extend(f)
        except Exception as e:
            warnings.append({"chain": cid, "message": str(e)})
            
    score_res = score(findings)
    
    # Graph building
    nodes = {}
    edges = []
    
    addr_type = "contract" if is_addr_contract else "wallet"
    if address in scam_list:
        addr_type = "flagged_address"
        
    nodes[address] = {"id": address, "label": address[:6] + "..." + address[-4:], "type": addr_type}
    
    # from findings evidence, we might extract counterparties
    # But a simple graph is already extracted by wallet_signals.
    # We can reconstruct it from findings, or we can just parse evidence strings (hacky).
    # Since we need to show interactions, let's just parse it.
    for f in findings:
        for ev in f.get('evidence', []):
            detail = ev.get('detail', '')
            # Try to find a 42-hex address in detail
            import re
            cps = re.findall(r'0x[a-fA-F0-9]{40}', detail)
            for cp in cps:
                cp = cp.lower()
                if cp != address:
                    t = "risky_contract" if f['signal_id'] in ('risky_contract_interaction', 'upgradeable_proxy') else "flagged_address"
                    if t == "flagged_address" and cp not in scam_list:
                        t = "contract" # default fallback
                    nodes[cp] = {"id": cp, "label": cp[:6] + "..." + cp[-4:], "type": t}
                    
                    edges.append({"source": address, "target": cp, "label": f['title']})
                    
    # Ensure graph format
    graph = {
        "nodes": list(nodes.values()),
        "edges": [dict(t) for t in {tuple(d.items()) for d in edges}] # unique edges
    }
    
    summary_text = ""
    if use_summary:
        summary_text = write_summary(findings)
        
    return {
        "address": address,
        "address_type": "contract" if is_addr_contract else "wallet",
        "chains": chain_ids,
        "overall_risk": score_res["overall_risk"],
        "score": score_res["score"],
        "points": score_res["points"],
        "signals": findings,
        "graph": graph,
        "summary": summary_text,
        "history_truncated": False,
        "warnings": warnings,
        "generated_at": start_time,
        "cache": {"hit": False, "saved_at": start_time}
    }
