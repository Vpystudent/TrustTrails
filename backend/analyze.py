import time
import json
import os
import re
from datetime import datetime, timezone
from backend.chains import is_contract, get_txs, get_token_transfers, get_approval_logs
from backend.wallet_signals import run as run_wallet_signals, load_scam_list, get_latest_approvals
from backend.contract_signals import check_contract
from backend.scoring import score
from backend.summary import write_summary

def validate_address(address: str) -> bool:
    if not address or not isinstance(address, str): return False
    return address.startswith('0x') and len(address) == 42 and all(c in '0123456789abcdefABCDEFx' for c in address)

def safe_int(val, default=0):
    if not val:
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        val = val.strip()
        if val.startswith('0x'):
            return int(val, 16)
        return int(val, 10)
    return default

def analyze(address: str, chain_ids: list, use_summary=True):
    address = address.lower()
    if not validate_address(address):
        raise ValueError("Invalid address format")
        
    start_time = datetime.now(timezone.utc).isoformat()
    findings = []
    warnings = []
    
    is_addr_contract = False
    scam_list = load_scam_list()
    
    coverage = {"chains": {}}
    approvals_list = []
    timeline_events = []
    all_txs_for_timeline = []

    for cid in chain_ids:
        c_ok = True
        c_truncated = False
        txs = []
        token_txs = []
        first_seen = None
        last_seen = None

        try:
            is_c = is_contract(address, cid)
            if is_c:
                is_addr_contract = True
                f = check_contract(address, cid)
                findings.extend(f)
            else:
                f = run_wallet_signals(address, cid)
                findings.extend(f)

            txs = get_txs(address, cid)
            token_txs = get_token_transfers(address, cid)
            
            if len(txs) == 10000 or len(token_txs) == 10000:
                c_truncated = True

            all_c_txs = txs + token_txs
            if all_c_txs:
                sorted_txs = sorted(all_c_txs, key=lambda x: safe_int(x.get('timeStamp', '0')))
                first_seen = datetime.fromtimestamp(safe_int(sorted_txs[0].get('timeStamp', '0')), timezone.utc).isoformat()
                last_seen = datetime.fromtimestamp(safe_int(sorted_txs[-1].get('timeStamp', '0')), timezone.utc).isoformat()
                
                for t in sorted_txs:
                    ts = safe_int(t.get('timeStamp', '0'))
                    all_txs_for_timeline.append({"ts": ts, "chain": cid, "hash": t.get("hash")})
            
            logs = get_approval_logs(address, cid)
            if logs:
                logs_desc = list(reversed(logs))
                latest_approvals, _ = get_latest_approvals(logs_desc)
                
                for (token, spender), log in latest_approvals.items():
                    data = log.get('data', '0x')
                    try:
                        amt = int(data, 16) if data != '0x' else 0
                    except:
                        amt = 0
                    
                    if amt > 0:
                        approvals_list.append({
                            "chain": cid,
                            "token": token,
                            "token_symbol": "Unknown", 
                            "spender": spender,
                            "spender_verified": False, 
                            "spender_is_contract": True,
                            "amount": "unlimited" if amt >= 2**255 else str(amt),
                            "live": True, 
                            "tx_hash": log.get('transactionHash')
                        })
                        
                        ts_val = log.get('timeStamp')
                        if not ts_val:
                            ts_val = log.get('blockNumber', '0')
                            
                        timeline_events.append({
                            "ts": safe_int(ts_val), 
                            "type": "unlimited_approval" if amt >= 2**255 else "approval",
                            "tx_hash": log.get('transactionHash'),
                            "chain": cid
                        })

        except Exception as e:
            c_ok = False
            warnings.append({"chain": cid, "message": str(e)})

        coverage["chains"][cid] = {
            "transactions": len(txs),
            "token_transfers": len(token_txs),
            "first_seen": first_seen,
            "last_seen": last_seen,
            "truncated": c_truncated,
            "ok": c_ok
        }

    score_res = score(findings)
    
    timeline_dict = {}
    for tx in all_txs_for_timeline:
        dt = datetime.fromtimestamp(tx["ts"], timezone.utc)
        month_key = dt.strftime("%Y-%m")
        if month_key not in timeline_dict:
            timeline_dict[month_key] = {"month": month_key, "transactions": 0, "events": []}
        timeline_dict[month_key]["transactions"] += 1
        
    for ev in timeline_events:
        dt = datetime.fromtimestamp(ev["ts"], timezone.utc)
        month_key = dt.strftime("%Y-%m")
        if month_key in timeline_dict:
            timeline_dict[month_key]["events"].append({
                "type": ev["type"],
                "tx_hash": ev["tx_hash"],
                "chain": ev["chain"]
            })

    timeline = sorted(list(timeline_dict.values()), key=lambda x: x["month"])
    
    nodes = {}
    edges = []
    
    nodes[address] = {"id": address, "label": address[:6] + "..." + address[-4:], "type": "target"}
    
    for f in findings:
        for ev in f.get('evidence', []):
            detail = ev.get('detail', '')
            cps = re.findall(r'0x[a-fA-F0-9]{40}', detail)
            for cp in cps:
                cp = cp.lower()
                if cp != address:
                    t = "risky_contract" if f['signal_id'] in ('risky_contract_interaction', 'upgradeable_proxy') else "flagged_address"
                    if t == "flagged_address" and cp not in scam_list:
                        t = "contract" 
                    nodes[cp] = {"id": cp, "label": cp[:6] + "..." + cp[-4:], "type": t}
                    edges.append({"source": address, "target": cp, "label": f['title']})
                    
    graph = {
        "nodes": list(nodes.values()),
        "edges": [dict(t) for t in {tuple(d.items()) for d in edges}]
    }
    
    summary_text = ''
    summary_status = 'disabled'
    if use_summary:
        s_res = write_summary(findings)
        summary_text = s_res['summary']
        summary_status = s_res['status']
        
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
        "summary_status": summary_status,
        "history_truncated": any(c["truncated"] for c in coverage["chains"].values()),
        "warnings": warnings,
        "generated_at": start_time,
        "cache": {"hit": False, "saved_at": start_time},
        "coverage": coverage,
        "approvals": approvals_list,
        "timeline": timeline
    }

