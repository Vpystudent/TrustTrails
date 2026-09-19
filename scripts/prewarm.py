import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.analyze import analyze

def run():
    demo_file = os.path.join(os.path.dirname(__file__), '..', 'backend', 'demo_addresses.json')
    if not os.path.exists(demo_file):
        with open(demo_file, 'w') as f:
            json.dump([
                {"label": "Safe Protocol (USDC)", "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "chains": ["ethereum"]},
                {"label": "Scam Wallet", "address": "TODO_FILL_ME", "chains": ["ethereum", "base"]},
                {"label": "Live Unlimited Approval", "address": "TODO_FILL_ME", "chains": ["ethereum", "base"]}
            ], f, indent=2)
            
    with open(demo_file, 'r') as f:
        demos = json.load(f)
        
    for d in demos:
        addr = d['address']
        if addr == "TODO_FILL_ME" or not addr.startswith("0x"):
            print(f"Skipping {d['label']}")
            continue
            
        print(f"Prewarming {addr} on {d['chains']}...")
        try:
            report = analyze(addr, d['chains'], use_summary=False)
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'cache', 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            cache_path = os.path.join(reports_dir, f"{addr.lower()}.json")
            with open(cache_path, "w") as rf:
                json.dump(report, rf, indent=2)
            print(f"Saved {addr}")
        except Exception as e:
            print(f"Error on {addr}: {e}")

if __name__ == '__main__':
    run()
