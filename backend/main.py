import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TrustTrail API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/chains")
def get_chains():
    return [
        {
            "id": "ethereum",
            "name": "Ethereum",
            "explorer_tx_url": "https://etherscan.io/tx/{h}",
            "explorer_addr_url": "https://etherscan.io/address/{a}"
        },
        {
            "id": "base",
            "name": "Base",
            "explorer_tx_url": "https://basescan.org/tx/{h}",
            "explorer_addr_url": "https://basescan.org/address/{a}"
        }
    ]

@app.get("/report")
def get_report(address: str = "", chains: str = "ethereum,base", summary: str = "true"):
    mock_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock", "report.json")
    with open(mock_path, "r") as f:
        return json.load(f)
