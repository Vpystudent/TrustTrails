import os
import requests
from backend.config import CHAINS
from backend.cache import fetch
from eth_hash.auto import keccak

MAX_RECORDS = 10000

def get_selector(signature: str) -> str:
    return "0x" + keccak(signature.encode("utf-8"))[:4].hex()

def get_topic(signature: str) -> str:
    return "0x" + keccak(signature.encode("utf-8")).hex()

APPROVAL_TOPIC = get_topic("Approval(address,address,uint256)")
APPROVAL_FOR_ALL_TOPIC = get_topic("ApprovalForAll(address,address,bool)")
ALLOWANCE_SELECTOR = get_selector("allowance(address,address)")

def pad_address(address: str) -> str:
    return "0x000000000000000000000000" + address.lower().replace("0x", "")

def fetch_etherscan_paginated(url, params, max_records=MAX_RECORDS):
    all_results = []
    page = 1
    offset = 1000
    while len(all_results) < max_records:
        params['page'] = page
        params['offset'] = offset
        data = fetch(url, params=params, provider='etherscan')
        if not data or data.get('status') != '1':
            break
        result = data.get('result', [])
        if not isinstance(result, list):
            break
        all_results.extend(result)
        if len(result) < offset:
            break
        page += 1
    return all_results[:max_records]

def fetch_blockscout_paginated(base_url, endpoint, max_records=MAX_RECORDS):
    all_results = []
    url = f"{base_url}/v2/{endpoint}"
    params = {}
    while len(all_results) < max_records:
        data = fetch(url, params=params, provider='blockscout')
        if not data:
            break
        items = data.get('items', [])
        all_results.extend(items)
        next_page = data.get('next_page_params')
        if not next_page:
            break
        params = next_page
        if len(all_results) >= max_records:
            break
    return all_results[:max_records]

def get_txs(address: str, chain_id: str):
    address = address.lower()
    chain = CHAINS[chain_id]
    if chain['history_provider'] == 'etherscan':
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "sort": "desc",
            "apikey": os.getenv("ETHERSCAN_API_KEY", ""),
            "chainid": chain['chainid']
        }
        return fetch_etherscan_paginated(chain['base_url'], params)
    else:
        return fetch_blockscout_paginated(chain['base_url'], f"addresses/{address}/transactions")

def get_token_transfers(address: str, chain_id: str):
    address = address.lower()
    chain = CHAINS[chain_id]
    if chain['history_provider'] == 'etherscan':
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "sort": "desc",
            "apikey": os.getenv("ETHERSCAN_API_KEY", ""),
            "chainid": chain['chainid']
        }
        return fetch_etherscan_paginated(chain['base_url'], params)
    else:
        return fetch_blockscout_paginated(chain['base_url'], f"addresses/{address}/token-transfers")

def get_approval_logs(address: str, chain_id: str):
    address = address.lower()
    padded_address = pad_address(address)
    chain = CHAINS[chain_id]
    
    # We fetch Approval and ApprovalForAll separately
    logs = []
    
    if chain['history_provider'] == 'etherscan':
        # Approval
        params = {
            "module": "logs",
            "action": "getLogs",
            "fromBlock": "0",
            "toBlock": "latest",
            "topic0": APPROVAL_TOPIC,
            "topic0_1_opr": "and",
            "topic1": padded_address,
            "apikey": os.getenv("ETHERSCAN_API_KEY", ""),
            "chainid": chain['chainid']
        }
        logs.extend(fetch_etherscan_paginated(chain['base_url'], params))
        
        # ApprovalForAll
        params["topic0"] = APPROVAL_FOR_ALL_TOPIC
        logs.extend(fetch_etherscan_paginated(chain['base_url'], params))
    else:
        # Blockscout RPC fallback?
        # Blockscout has /api?module=logs&action=getLogs but it's Etherscan compatible
        # So we can just use the etherscan approach on blockscout API
        params = {
            "module": "logs",
            "action": "getLogs",
            "fromBlock": "0",
            "toBlock": "latest",
            "topic0": APPROVAL_TOPIC,
            "topic0_1_opr": "and",
            "topic1": padded_address
        }
        url = chain['base_url']
        # For blockscout, the V1 etherscan api endpoint is usually just base_url (which is /api)
        def fetch_blockscout_logs(p):
            data = fetch(url, params=p, provider='blockscout')
            if data and data.get('status') == '1' and isinstance(data.get('result'), list):
                return data.get('result')
            return []
            
        logs.extend(fetch_blockscout_logs(params))
        params["topic0"] = APPROVAL_FOR_ALL_TOPIC
        logs.extend(fetch_blockscout_logs(params))
        
    return logs

def rpc_call(chain_id, method, params):
    chain = CHAINS[chain_id]
    url = chain['rpc_url']
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    data = fetch(url, json_data=payload, method="POST", provider="rpc")
    if data and "result" in data:
        return data["result"]
    return None

def get_allowance(token: str, owner: str, spender: str, chain_id: str) -> int:
    token = token.lower()
    owner = owner.lower()
    spender = spender.lower()
    data = ALLOWANCE_SELECTOR + pad_address(owner).replace("0x", "") + pad_address(spender).replace("0x", "")
    result = rpc_call(chain_id, "eth_call", [{"to": token, "data": data}, "latest"])
    if result and result != "0x":
        try:
            return int(result, 16)
        except ValueError:
            return 0
    return 0

def get_code(address: str, chain_id: str) -> str:
    address = address.lower()
    result = rpc_call(chain_id, "eth_getCode", [address, "latest"])
    return result if result else "0x"

def is_contract(address: str, chain_id: str) -> bool:
    code = get_code(address, chain_id)
    return code != "0x" and code != "0x0"

def get_storage_at(address: str, slot: str, chain_id: str) -> str:
    address = address.lower()
    result = rpc_call(chain_id, "eth_getStorageAt", [address, slot, "latest"])
    return result if result else "0x0"

def get_source(address: str, chain_id: str):
    address = address.lower()
    chain = CHAINS[chain_id]
    # Etherscan compatible for both
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address
    }
    if chain['history_provider'] == 'etherscan':
        params['apikey'] = os.getenv("ETHERSCAN_API_KEY", "")
        params['chainid'] = chain['chainid']
        url = chain['base_url']
    else:
        url = chain['base_url']
        
    data = fetch(url, params=params, provider=chain['history_provider'])
    if data and data.get('status') == '1':
        return data.get('result', [])
    return []

def get_contract_creation(address: str, chain_id: str):
    address = address.lower()
    chain = CHAINS[chain_id]
    params = {
        "module": "contract",
        "action": "getcontractcreation",
        "contractaddresses": address
    }
    if chain['history_provider'] == 'etherscan':
        params['apikey'] = os.getenv("ETHERSCAN_API_KEY", "")
        params['chainid'] = chain['chainid']
        url = chain['base_url']
    else:
        url = chain['base_url']
        
    data = fetch(url, params=params, provider=chain['history_provider'])
    if data and data.get('status') == '1':
        res = data.get('result', [])
        if res and isinstance(res, list):
            return res[0]
    return None
