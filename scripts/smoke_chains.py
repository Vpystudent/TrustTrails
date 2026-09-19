import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import CHAINS
from backend.cache import fetch

def test_api(chain_name, address):
    print(f"Testing {chain_name} on {address}...")
    chain = CHAINS[chain_name]
    
    # txs
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "page": 1,
        "offset": 5,
        "sort": "asc",
    }
    if chain['history_provider'] == 'etherscan':
        params['apikey'] = os.getenv("ETHERSCAN_API_KEY", "")
        params['chainid'] = chain['chainid']
        url = chain['base_url']
    else:
        url = chain['base_url'] + f"/v2/addresses/{address}/transactions"
        params = {}
    
    data = fetch(url, params=params, provider=chain['history_provider'])
    print("Ethereum Etherscan message:", data.get("message"))
    print("Ethereum Etherscan result type:", type(data.get("result")))
    if isinstance(data.get("result"), list):
        print("Length:", len(data.get("result")))
    else:
        print("Result:", data.get("result"))

if __name__ == '__main__':
    test_api('ethereum', '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045') # vitalik
