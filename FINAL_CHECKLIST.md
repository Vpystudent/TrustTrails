# TrustTrail Final Checklist

## 1. Environment Setup
- [ ] Run cp .env.example .env and populate ETHERSCAN_API_KEY and LLM_API_KEY.
- [ ] Verify LLM_BASE_URL and LLM_MODEL match your Google AI Studio configuration.

## 2. Generate Data
- [ ] Run python scripts/make_labels.py to download the ScamSniffer database.
- [ ] Run python scripts/make_safe_labels.py to generate safe protocol addresses.

## 3. Prewarm Cache (Optional but recommended for demos)
- [ ] Edit ackend/demo_addresses.json to insert real address targets.
- [ ] Run python scripts/prewarm.py to fetch and store reports.

## 4. Launch Application
- [ ] Run python scripts/run_dev.py.
- [ ] Verify frontend loads at http://localhost:5173.
- [ ] Verify backend is healthy at http://localhost:8000/health.

## 5. UI Verification (Human Steps)
- [ ] Input a safe protocol address and verify the "No risk signals found" green card.
- [ ] Input a scam wallet (from ackend/labels/scam_test.csv) and verify red high-risk UI.
- [ ] Click a node in the Evidence Graph to verify it opens the explorer.
- [ ] Click "Use sample report" with backend stopped or OFFLINE=1 to verify offline mode works.
