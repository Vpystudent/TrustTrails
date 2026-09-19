import json
import time
import os
from datetime import datetime, timezone
from backend.chains import get_txs, get_token_transfers, get_approval_logs, get_allowance
from backend.contract_signals import check_contract

_scam_list = None
_scam_list_date = None

def load_scam_list():
    global _scam_list, _scam_list_date
    if _scam_list is not None:
        return _scam_list, _scam_list_date
    scam_file = os.path.join(os.path.dirname(__file__), "labels", "scam_signal.csv")
    scams = {}
    if os.path.exists(scam_file):
        _scam_list_date = datetime.fromtimestamp(os.path.getmtime(scam_file), timezone.utc).strftime('%Y-%m-%d')
        with open(scam_file, "r") as f:
            for i, line in enumerate(f):
                if i == 0: continue
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    addr = parts[0].strip().lower()
                    if addr:
                        scams[addr] = {"row": i, "label": parts[1], "source": parts[2]}
    _scam_list = scams
    return scams, _scam_list_date

def get_latest_approvals(logs):
    latest_approvals = {}
    latest_nfts = {}
    
    for log in logs:
        topics = log.get('topics', [])
        if len(topics) < 3:
            continue
            
        topic0 = topics[0]
        spender = "0x" + topics[2][26:]
        token = log.get('address', '').lower()
        
        if topic0.startswith("0x8c5be1e5"):
            if (token, spender) not in latest_approvals:
                latest_approvals[(token, spender)] = log
        elif topic0.startswith("0x17307eab"):
            if (token, spender) not in latest_nfts:
                latest_nfts[(token, spender)] = log
                
    return latest_approvals, latest_nfts

def run(address: str, chain_id: str):
    address = address.lower()
    findings = []
    scam_list, scam_date = load_scam_list()
    
    txs = get_txs(address, chain_id)
    token_txs = get_token_transfers(address, chain_id)
    
    if address in scam_list:
        ev = [{"detail": "Evidence: third-party list (ScamSniffer)", "source": scam_list[address]["source"], "snapshot": scam_date, "row_reference": scam_list[address]["row"]}]
        all_txs = txs + token_txs
        if all_txs:
            for t in all_txs[:5]:
                ev.append({"tx_hash": t.get("hash"), "block": int(t.get("blockNumber", "0")), "detail": "On-chain activity by this flagged address."})
                
        findings.append({
            "signal_id": "flagged_address",
            "severity": "high",
            "score": 1.0,
            "chain": chain_id,
            "title": "Address on a known-scam list",
            "evidence": ev,
            "rule": f"This address appears on the ScamSniffer phishing address list (snapshot {scam_date})"
        })
        
    logs = get_approval_logs(address, chain_id)
    logs_desc = list(reversed(logs))
    latest_approvals, latest_nfts = get_latest_approvals(logs_desc)
    
    for (token, spender), log in latest_approvals.items():
        data = log.get('data', '0x')
        try:
            amount = int(data, 16) if data != '0x' else 0
        except ValueError:
            amount = 0
            
        if amount >= 2**255:
            allowance = get_allowance(token, address, spender, chain_id)
            if allowance > 0:
                spender_findings = check_contract(spender, chain_id)
                high_risk = spender in scam_list
                for sf in spender_findings:
                    if sf['signal_id'] in ('unverified_contract', 'upgradeable_proxy'):
                        high_risk = True
                
                severity = "high" if high_risk else "medium"
                findings.append({
                    "signal_id": "unlimited_approval",
                    "severity": severity,
                    "score": 1.0 if severity == "high" else 0.75,
                    "chain": chain_id,
                    "title": "Unlimited Token Approval",
                    "evidence": [{"tx_hash": log.get('transactionHash'), "block": int(log.get('blockNumber', '0'), 16), "detail": f"Approved max uint256 to {spender}"}],
                    "rule": "Approval amount >= 2**255 and live allowance > 0."
                })
                
    for (token, spender), log in latest_nfts.items():
        data = log.get('data', '0x')
        try:
            approved = int(data, 16) > 0 if data != '0x' else False
        except ValueError:
            approved = False
            
        if approved:
            findings.append({
                "signal_id": "nft_approval_for_all",
                "severity": "medium",
                "score": 0.75,
                "chain": chain_id,
                "title": "NFT Approval For All",
                "evidence": [{"tx_hash": log.get('transactionHash'), "block": int(log.get('blockNumber', '0'), 16), "detail": f"Granted ApprovalForAll to {spender}"}],
                "rule": "Active ApprovalForAll granted."
            })
            
    counterparties = set()
    scam_interactions = {}
    
    def add_interaction(cp, tx_hash):
        if not cp: return
        cp = cp.lower()
        counterparties.add(cp)
        if cp in scam_list:
            if cp not in scam_interactions:
                scam_interactions[cp] = []
            scam_interactions[cp].append(tx_hash)
            
    for tx in txs:
        t_from = tx.get('from', '').lower()
        t_to = tx.get('to', '').lower()
        tx_hash = tx.get('hash', '')
        if t_from != address:
            add_interaction(t_from, tx_hash)
        if t_to and t_to != address:
            add_interaction(t_to, tx_hash)
            
    for tx in token_txs:
        t_from = tx.get('from', '').lower()
        t_to = tx.get('to', '').lower()
        tx_hash = tx.get('hash', '')
        if t_from != address:
            add_interaction(t_from, tx_hash)
        if t_to and t_to != address:
            add_interaction(t_to, tx_hash)
            
    for scam_cp, hashes in scam_interactions.items():
        findings.append({
            "signal_id": "flagged_counterparty",
            "severity": "high",
            "score": 1.0,
            "chain": chain_id,
            "title": "Interacted with Flagged Counterparty",
            "evidence": [{"tx_hash": h, "block": 0, "detail": f"Interacted with scam address {scam_cp}"} for h in list(set(hashes))[:5]],
            "rule": "Any tx or token-transfer counterparty in the scam list."
        })
        
    if txs:
        first_tx = txs[-1] if txs else None
        if first_tx:
            timestamp = int(first_tx.get('timeStamp', '0'))
            now = time.time()
            if (now - timestamp) < 7 * 24 * 3600:
                incoming_senders = set()
                for tx in txs:
                    if tx.get('to', '').lower() == address:
                        incoming_senders.add(tx.get('from', '').lower())
                if len(incoming_senders) >= 10:
                    findings.append({
                        "signal_id": "fresh_wallet_pattern",
                        "severity": "medium",
                        "score": 0.75,
                        "chain": chain_id,
                        "title": "Fresh Wallet Pattern",
                        "evidence": [{"tx_hash": first_tx.get('hash', ''), "block": int(first_tx.get('blockNumber', '0')), "detail": f"First tx <7 days ago, {len(incoming_senders)} distinct senders"}],
                        "rule": "First tx under 7 days ago AND at least 10 distinct incoming senders."
                    })
                    
    cp_counts = {}
    for tx in txs:
        t_to = tx.get('to', '').lower()
        if t_to and t_to != address:
            if t_to not in cp_counts:
                cp_counts[t_to] = {'count': 0, 'last_tx': tx.get('hash', ''), 'timestamp': int(tx.get('timeStamp', '0'))}
            cp_counts[t_to]['count'] += 1
            ts = int(tx.get('timeStamp', '0'))
            if ts > cp_counts[t_to]['timestamp']:
                cp_counts[t_to]['timestamp'] = ts
                cp_counts[t_to]['last_tx'] = tx.get('hash', '')
                
    sorted_cps = sorted(cp_counts.items(), key=lambda x: (-x[1]['count'], -x[1]['timestamp']))[:15]
    for cp, data in sorted_cps:
        cf = check_contract(cp, chain_id)
        for f in cf:
            if f['severity'] == 'high':
                findings.append({
                    "signal_id": "risky_contract_interaction",
                    "severity": "high",
                    "score": 1.0,
                    "chain": chain_id,
                    "title": "Interaction with Risky Contract",
                    "evidence": [{"tx_hash": data['last_tx'], "block": 0, "detail": f"Contract {cp} flagged as: {f['title']}"}],
                    "rule": "Counterparty contract flagged with high severity."
                })
                break
                
    return findings
