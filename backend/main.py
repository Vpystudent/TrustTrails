import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.config import CHAINS, OFFLINE
from backend.analyze import analyze

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
    return list(CHAINS.values())

@app.get("/report")
def get_report(address: str = "", chains: str = "ethereum,base", summary: str = "true"):
    address = address.lower()
    if len(address) != 42 or not address.startswith("0x"):
        raise HTTPException(status_code=400, detail="Invalid address")
        
    use_summary = summary.lower() == "true"
    chain_list = [c.strip() for c in chains.split(",")]
    
    reports_dir = os.path.join(os.path.dirname(__file__), "cache", "reports")
    cache_path = os.path.join(reports_dir, f"{address}.json")
    
    if OFFLINE:
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                data["cache"]["hit"] = True
                return data
        raise HTTPException(status_code=404, detail="Report not found in offline cache")
        
    try:
        report = analyze(address, chain_list, use_summary=use_summary)
        
        os.makedirs(reports_dir, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
