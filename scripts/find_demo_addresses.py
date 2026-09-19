import json
import random
import os
import sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.chains import get_txs, get_token_transfers

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

def main():
    scam_csv = os.path.join(os.path.dirname(__file__), '..', 'backend', 'labels', 'scam_signal.csv')
    scams = []
    snapshot = datetime.fromtimestamp(os.path.getmtime(scam_csv), timezone.utc).strftime('%Y-%m-%d')
    with open(scam_csv, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 0: continue
            parts = line.strip().split(',')
            if len(parts) >= 3 and parts[0]:
                scams.append(parts[0].strip().lower())
                
    random.seed(42)
    sample = random.sample(scams, min(150, len(scams)))
    
    candidates = []
    chains = ['ethereum', 'base', 'arbitrum']
    
    print(f"Testing {len(sample)} sampled addresses...")
    
    for addr in sample:
        if len(candidates) >= 3:
            break
            
        print(f"Checking {addr}...")
        tx_counts = {}
        chains_with_activity = []
        first_seen = None
        last_seen = None
        distinct_senders = set()
        
        has_enough = False
        
        for c in chains:
            try:
                txs = get_txs(addr, c)
                tt = get_token_transfers(addr, c)
            except Exception as e:
                print(f"Error on {c}: {e}")
                continue
                
            total = len(txs) + len(tt)
            tx_counts[c] = total
            
            if total >= 15:
                has_enough = True
                
            if total > 0:
                chains_with_activity.append(c)
                all_txs = txs + tt
                sorted_txs = sorted(all_txs, key=lambda x: safe_int(x.get('timeStamp', '0')))
                
                c_first = datetime.fromtimestamp(safe_int(sorted_txs[0].get('timeStamp', '0')), timezone.utc).isoformat()
                c_last = datetime.fromtimestamp(safe_int(sorted_txs[-1].get('timeStamp', '0')), timezone.utc).isoformat()
                
                if not first_seen or c_first < first_seen: first_seen = c_first
                if not last_seen or c_last > last_seen: last_seen = c_last
                
                for t in txs:
                    if t.get('to', '').lower() == addr:
                        distinct_senders.add(t.get('from', '').lower())
                        
        if has_enough:
            candidates.append({
                "address": addr,
                "chains_with_activity": chains_with_activity,
                "tx_counts": tx_counts,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "distinct_senders": len(distinct_senders),
                "source": "scamsniffer",
                "snapshot": snapshot
            })
            print(f"Found candidate: {addr} with {tx_counts}")
            
    with open(os.path.join(os.path.dirname(__file__), '..', 'backend', 'demo_candidates.json'), 'w') as f:
        json.dump(candidates, f, indent=2)
        
    for c in candidates:
        print(f"\nAddress: {c['address']}")
        print(f"Activity: {c['tx_counts']}")
        if 'ethereum' in c['chains_with_activity']:
            print(f"Etherscan: https://etherscan.io/address/{c['address']}")
        if 'base' in c['chains_with_activity']:
            print(f"Basescan: https://basescan.org/address/{c['address']}")
        if 'arbitrum' in c['chains_with_activity']:
            print(f"Arbiscan: https://arbiscan.io/address/{c['address']}")

if __name__ == '__main__':
    main()
