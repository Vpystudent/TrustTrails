import json
import os
import random
from datetime import datetime

address = "0x6666666666666666666666666666666666666666"

nodes = [{"id": address, "label": "Lazarus Group (Main)", "type": "target"}]
edges = []
evidence = []

for i in range(50):
    mixer = f"0x000000000000000000000000000000000000{i:04x}"
    nodes.append({"id": mixer, "label": f"Tornado Router {i}", "type": "risky_contract"})
    edges.append({"source": address, "target": mixer, "label": "0.1 ETH"})
    evidence.append({"detail": f"Interacted with known mixer", "tx_hash": f"0xabc{i}", "block": 15000000+i, "counterparty": mixer})
    if i > 0:
        edges.append({"source": mixer, "target": f"0x000000000000000000000000000000000000{(i-1):04x}", "label": "wash"})

for i in range(20):
    victim = f"0x111111111111111111111111111111111111{i:04x}"
    nodes.append({"id": victim, "label": f"Exploited Victim {i}", "type": "wallet"})
    edges.append({"source": victim, "target": address, "label": "1000 ETH (Stolen)"})
    evidence.append({"detail": f"Received funds from exploited contract", "tx_hash": f"0xdef{i}", "block": 14000000+i, "counterparty": victim})

for i in range(10):
    fake = f"0x222222222222222222222222222222222222{i:04x}"
    nodes.append({"id": fake, "label": f"Fake Phishing Token {i}", "type": "contract"})
    edges.append({"source": address, "target": fake, "label": "Deploy"})
    evidence.append({"detail": f"Deployed malicious contract", "tx_hash": f"0x123{i}", "block": 16000000+i, "counterparty": fake})

for i in range(20):
    fake = f"0x222222222222222222222222222222222222{random.randint(0,9):04x}"
    victim = f"0x111111111111111111111111111111111111{i:04x}"
    edges.append({"source": victim, "target": fake, "label": "Approve (Malicious)"})

report = {
  "address": address,
  "chains": ["ethereum"],
  "signals": [
    {
      "signal_id": "massive_laundering_ring",
      "chain": "ethereum",
      "severity": "high",
      "title": "Massive Money Laundering Ring",
      "rule": "Address exhibits extreme wash-trading and mixing topology.",
      "evidence": evidence
    }
  ],
  "points": [
    {"signal_id": "massive_laundering_ring", "points": 100, "reason": "Central hub for 50+ mixers and stolen funds."}
  ],
  "score": 100,
  "overall_risk": "high",
  "history_truncated": True,
  "warnings": [],
  "graph": {
    "nodes": nodes,
    "edges": edges
  },
  "summary": "This address represents a highly sophisticated cybercriminal hub (likely Lazarus Group). The interaction graph reveals a massive star topology where stolen funds from 20+ victims are routed into a central wallet, which then systematically disperses the assets across 50 different mixer contracts (like Tornado Cash) to obfuscate the trail. The address also acts as an active deployer for fake phishing tokens designed to trick retail users into malicious approvals.",
  "generated_at": datetime.now().isoformat(),
  "cache": {"hit": True},
  "coverage": {
    "chains": {
        "ethereum": {
            "transactions": 10000,
            "token_transfers": 10000,
            "first_seen": "2020-01-01T00:00:00Z",
            "last_seen": "2026-01-01T00:00:00Z",
            "truncated": True,
            "ok": True
        }
    }
  },
  "approvals": [],
  "timeline": [{"month": "2023-01", "transactions": 500, "events": []}]
}

os.makedirs("backend/cache/reports", exist_ok=True)
with open(f"backend/cache/reports/{address}.json", "w") as f:
    json.dump(report, f, indent=2)
