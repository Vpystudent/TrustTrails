# TrustTrail ???

**TrustTrail** is a next-generation, cross-chain risk analysis engine designed to democratize Web3 security. 

It acts as an automated forensic investigator: drop in any wallet or smart contract address, and it scans the entire interaction history across multiple blockchains (Ethereum, Base, Arbitrum) to generate an instant, human-readable risk report. 

Every single risk flag is backed by **cryptographic proof** (on-chain transaction hashes, block numbers, and smart contract state).

---

## ?? Hackathon Judging Criteria Alignment

### 1. Innovation & Problem Impact ??
Web3 security today is fragmented. Users either stare at a block explorer (which is just a wall of raw hex data) or pay thousands of dollars for enterprise forensics tools. TrustTrail solves this by translating complex on-chain interactions into a simple 0-100 Trust Score. It detects chronic security hygiene issues (like open unlimited token approvals) and actively maps out money laundering topologies instantly.

### 2. Security & Trustlessness ??
**The AI Firewall:** Judges often worry about AI hallucinating security scores. In TrustTrail, the AI has **absolutely zero control over the risk score**. The scoring engine is 100% deterministic, rule-based Python math. We only use the LLM (Google AI Studio) at the very end of the pipeline as a *translator* to narrate the finalized JSON report into a plain-English paragraph.

### 3. Solution Design & User Experience ??
TrustTrail features a gorgeous, dark-mode React UI with tailored empty states, Loading skeletons, and smooth CSS transitions. We integrated **Cytoscape.js** to provide a physics-based, dynamic Interaction Graph that visually maps out how victim wallets interact with malicious contracts and laundering rings. 

### 4. Technical Excellence & Efficiency ?
- **Multi-Provider Data Layer:** The engine seamlessly normalizes data across different schemas (Etherscan V2 for Ethereum/Arbitrum, Blockscout V2 for Base).
- **Custom Caching Engine:** To survive strict free-tier API rate limits during the hackathon, we built a custom SQLite caching layer that spaces every API request by exactly 0.25 seconds and gracefully retries 429 errors.
- **On-chain State Checks:** We don't just rely on APIs. The engine uses RPC nodes to manually inspect memory slots (e.g. checking EIP-1967 slots to see if a contract is a proxy).

### 5. Testing & Code Quality ??
The project is built with clean, modular Python and React code. It includes an automated test suite (pytest) to ensure the scoring engine's mathematical invariants always hold (e.g., points always sum correctly). It also includes a custom evaluation script (un_eval.py) that tests the engine's recall and precision against a blind dataset of known scams with explicit blacklists disabled.

### 6. Accessibility ?
The UI includes semantic HTML, proper contrast ratios, and ria-labels on interactive elements to ensure accessibility standards are met.

---

## ?? Architecture

\\\mermaid
flowchart TD
    Client[React Frontend] -->|GET /report| API[FastAPI Backend]
    API --> Cache[(SQLite Cache Layer)]
    API --> Analyze[Analyze Engine]
    Analyze --> WS[Wallet Signals]
    Analyze --> CS[Contract Signals]
    Analyze --> LLM[Google AI Studio]
    WS --> Etherscan[Etherscan API V2]
    WS --> Blockscout[Blockscout API V2]
    CS --> RPC[Ethereum & Base RPC]
\\\

## ?? Setup & Installation

### Backend Setup
1. Create a virtual environment: python -m venv venv
2. Activate it: .\\venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)
3. Install dependencies: pip install -r requirements.txt
4. Copy .env.example to .env and fill in your keys (Etherscan, Google AI).

### Frontend Setup
1. Navigate to the frontend directory: cd frontend
2. Install dependencies: 
pm install

## ?? Running the Application

For the live demo, start both servers in separate terminal windows:

**Terminal 1 (Backend API):**
\\\ash
.\\venv\\Scripts\\uvicorn backend.main:app --host 0.0.0.0 --port 8000
\\\

**Terminal 2 (Frontend UI):**
\\\ash
cd frontend
npm run dev
\\\

Open [http://localhost:5173](http://localhost:5173) to view the app!

## ?? Testing

Run the automated test suite to verify the scoring and signal heuristics:
\\\ash
pytest
\\\

## ?? Known Limitations
- **EVM Only**: Only supports EVM-compatible chains.
- **Off-chain Signatures**: Cannot currently detect off-chain Permit signature approvals since they emit no logs until execution.
- **History Cap**: API paginates up to 10,000 records per address. Heavily active exchange hot wallets will trigger a "History Truncated" warning.
