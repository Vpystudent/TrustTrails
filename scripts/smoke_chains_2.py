import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.chains import get_txs, get_code, get_allowance, get_approval_logs

print('Base Txs (vitalik):', len(get_txs('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', 'base')))
print('Ethereum is_contract (USDC):', get_code('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'ethereum')[:20])
print('Base is_contract (USDbC):', get_code('0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA', 'base')[:20])
print('Ethereum Allowance (USDC, vitalik, vitalik):', get_allowance('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', 'ethereum'))
