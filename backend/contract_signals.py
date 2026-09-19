import time
import json
import os
import csv
from eth_hash.auto import keccak
from backend.chains import get_code, get_storage_at, get_source, get_contract_creation, rpc_call, is_contract, get_txs
from datetime import datetime, timezone

EIP1967_IMPL_SLOT = hex(int.from_bytes(keccak(b"eip1967.proxy.implementation"), "big") - 1)
EIP1967_ADMIN_SLOT = hex(int.from_bytes(keccak(b"eip1967.proxy.admin"), "big") - 1)

def get_selector(sig):
    return "0x" + keccak(sig.encode("utf-8"))[:4].hex()

OWNER_SELECTOR = get_selector("owner()")

_scam_list = None
_scam_list_date = None

def load_scam_list():
    global _scam_list, _scam_list_date
    if _scam_list is not None:
        return _scam_list, _scam_list_date
    labels_dir = os.path.join(os.path.dirname(__file__), 'labels')
    scam_csv = os.path.join(labels_dir, 'scam_signal.csv')
    scams = {}
    if os.path.exists(scam_csv):
        _scam_list_date = datetime.fromtimestamp(os.path.getmtime(scam_csv), timezone.utc).strftime('%Y-%m-%d')
        with open(scam_csv, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 0: continue
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    addr = parts[0].strip().lower()
                    if addr:
                        scams[addr] = {"row": i, "label": parts[1], "source": parts[2]}
    _scam_list = scams
    return scams, _scam_list_date

def get_owner(address, chain_id):
    res = rpc_call(chain_id, "eth_call", [{"to": address, "data": OWNER_SELECTOR}, "latest"])
    if res and len(res) >= 66:
        owner_addr = "0x" + res[-40:].lower()
        if owner_addr != "0x0000000000000000000000000000000000000000":
            return owner_addr
    return None

def check_contract(address, chain_id):
    address = address.lower()
    findings = []
    
    if not is_contract(address, chain_id):
        return findings
        
    scam_list, scam_date = load_scam_list()
    if address in scam_list:
        ev = [{"detail": "Evidence: third-party list (ScamSniffer)", "source": scam_list[address]["source"], "snapshot": scam_date, "row_reference": scam_list[address]["row"]}]
        txs = get_txs(address, chain_id)
        if txs:
            for t in txs[:5]:
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
        
    source_data = get_source(address, chain_id)
    source_info = source_data[0] if source_data else {}
    abi = source_info.get('ABI', '')
    proxy = source_info.get('Proxy', '0')
    implementation = source_info.get('Implementation', '')
    
    is_unverified = abi == 'Contract source code not verified'
    if is_unverified:
        findings.append({
            "signal_id": "unverified_contract",
            "severity": "medium",
            "score": 0.75,
            "chain": chain_id,
            "title": "Unverified Contract",
            "evidence": [{"tx_hash": "", "block": 0, "detail": "Contract source code is not verified on explorer."}],
            "rule": "Contract source code not verified."
        })
        
    impl_slot_val = get_storage_at(address, EIP1967_IMPL_SLOT, chain_id)
    is_eip1967 = impl_slot_val != "0x0" and int(impl_slot_val, 16) != 0
    if proxy == '1' or is_eip1967:
        actual_impl = implementation if proxy == '1' else "0x" + impl_slot_val[-40:]
        
        owner = get_owner(address, chain_id)
        if not owner and is_eip1967:
            admin_slot_val = get_storage_at(address, EIP1967_ADMIN_SLOT, chain_id)
            if admin_slot_val != "0x0" and int(admin_slot_val, 16) != 0:
                owner = "0x" + admin_slot_val[-40:]
                
        severity = "medium"
        detail_msg = f"Implementation: {actual_impl}"
        if owner:
            if not is_contract(owner, chain_id):
                severity = "high"
                detail_msg += f". Admin/Owner is a single EOA: {owner}."
            else:
                detail_msg += f". Admin/Owner is a contract: {owner}."
                
        findings.append({
            "signal_id": "upgradeable_proxy",
            "severity": severity,
            "score": 1.0 if severity == 'high' else 0.75,
            "chain": chain_id,
            "title": "Upgradeable Proxy",
            "evidence": [{"tx_hash": "", "block": 0, "detail": detail_msg}],
            "rule": "EIP-1967 slot non-zero OR getsourcecode Proxy/Implementation."
        })
        
    owner = get_owner(address, chain_id)
    if owner:
        if not is_contract(owner, chain_id):
            findings.append({
                "signal_id": "owner_privileges",
                "severity": "medium",
                "score": 0.75,
                "chain": chain_id,
                "title": "Owner Privileges",
                "evidence": [{"tx_hash": "", "block": 0, "detail": f"Owner {owner} is an EOA."}],
                "rule": "single key controls this contract."
            })
        else:
            findings.append({
                "signal_id": "owner_privileges",
                "severity": "low",
                "score": 0.5,
                "chain": chain_id,
                "title": "Owner Privileges",
                "evidence": [{"tx_hash": "", "block": 0, "detail": f"Owner {owner} is a contract."}],
                "rule": "contract controls this contract."
            })
            
    if not is_unverified and abi:
        try:
            abi_json = json.loads(abi)
            risky = []
            for item in abi_json:
                if item.get('type') == 'function':
                    name = item.get('name', '')
                    lname = name.lower()
                    if lname in ['mint', 'pause', 'unpause', 'blacklist', 'setowner'] or lname.startswith('setfee') or lname.startswith('settax') or lname.startswith('upgradeto'):
                        risky.append(name)
            if risky:
                findings.append({
                    "signal_id": "risky_functions",
                    "severity": "medium",
                    "score": 0.75,
                    "chain": chain_id,
                    "title": "Risky Functions",
                    "evidence": [{"tx_hash": "", "block": 0, "detail": f"Functions found: {', '.join(risky)}"}],
                    "rule": "Scan ABI for mint, pause, unpause, blacklist, setFee/setTax*, upgradeTo*, setOwner."
                })
        except:
            pass
            
    txs = get_txs(address, chain_id)
    if txs:
        oldest_tx = txs[-1]
        ts = int(oldest_tx.get('timeStamp', '0'))
        if ts > 0:
            if time.time() - ts < 30 * 24 * 3600:
                findings.append({
                    "signal_id": "new_contract",
                    "severity": "medium",
                    "score": 0.75,
                    "chain": chain_id,
                    "title": "New Contract",
                    "evidence": [{"tx_hash": oldest_tx.get('hash', ''), "block": 0, "detail": f"Created < 30 days ago (timestamp: {ts})"}],
                    "rule": "Created under 30 days ago."
                })
                
    return findings
