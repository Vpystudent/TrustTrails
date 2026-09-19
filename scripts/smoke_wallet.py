import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.wallet_signals import run

if __name__ == '__main__':
    address = sys.argv[1] if len(sys.argv) > 1 else "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    chain = sys.argv[2] if len(sys.argv) > 2 else "ethereum"
    findings = run(address, chain)
    print(json.dumps(findings, indent=2))
