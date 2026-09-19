# 🛡️ Trust Trails

**Trust Trails** is a next-generation, cross-chain risk analysis engine designed to democratize Web3 security.

Drop in any wallet or smart contract address, and it scans the entire interaction history across multiple blockchains (**Ethereum**, **Base**, **Arbitrum**) to generate an instant, human-readable risk report. Every single risk flag is backed by **cryptographic proof** — on-chain transaction hashes, block numbers, and smart contract state.

---

## 🎯 The Problem

Web3 security today is fragmented. Users either stare at a block explorer (a wall of raw hex data) or pay thousands of dollars for enterprise forensics tools. Trust Trails solves this by translating complex on-chain interactions into a simple **0–100 Trust Score** — detecting chronic security issues like unlimited token approvals and actively mapping money laundering topologies.

---

## ✨ Key Features

- **Cross-Chain Scanning** — Analyzes wallet and contract activity across Ethereum, Base, and Arbitrum simultaneously
- **Deterministic Trust Score (0–100)** — 100% rule-based scoring engine. The AI has zero control over the risk score
- **AI-Powered Summaries** — Google AI Studio narrates the final JSON report into a plain-English paragraph
- **Interactive Interaction Graph** — Cytoscape.js-powered physics-based visualization of wallet interactions and laundering rings
- **On-Chain Verification** — Direct RPC state inspection (e.g., EIP-1967 proxy detection via storage slots)
- **Smart Caching** — SQLite caching layer with rate-limit handling and automatic 429 retries
- **Evidence-Based** — Every risk flag links directly to an on-chain transaction hash or block number

---

## 🏗️ Architecture

```
┌──────────────┐       GET /report       ┌──────────────────┐
│              │ ──────────────────────▶  │                  │
│  React UI    │                         │  FastAPI Backend  │
│  (Vite)      │ ◀──────────────────────  │                  │
└──────────────┘       JSON Response     └────────┬─────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                             ┌───────────┐ ┌───────────┐ ┌─────────────┐
                             │  Wallet   │ │ Contract  │ │   Google    │
                             │  Signals  │ │  Signals  │ │  AI Studio  │
                             └─────┬─────┘ └─────┬─────┘ └─────────────┘
                                   │             │
                          ┌────────┴───┐    ┌────┴────┐
                          ▼            ▼    ▼         │
                    ┌───────────┐ ┌────────────┐ ┌────┴────┐
                    │ Etherscan │ │ Blockscout │ │  ETH &  │
                    │  API V2   │ │   API V2   │ │Base RPC │
                    └───────────┘ └────────────┘ └─────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm

### 1. Clone the Repository

```bash
git clone https://github.com/Vpystudent/TrustTrails.git
cd TrustTrails
```

### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
ETHERSCAN_API_KEY=your_etherscan_api_key
LLM_API_KEY=your_google_ai_studio_key
LLM_MODEL=gemini-3.8-flash
OFFLINE=0
```

> **Note:** Set `OFFLINE=1` to run in offline/mock mode using cached reports (no API keys needed for demo).

### 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## ▶️ Running the Application

Start both servers in **separate terminals**:

**Terminal 1 — Backend API:**

```bash
.\venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend UI:**

```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser to view the app.

---

## 🎮 Demo & Usage

### Built-in Demo Addresses

The UI includes one-click demo buttons to instantly analyze real addresses:

| Demo | Address | Chain | Source |
|------|---------|-------|--------|
| Safe Protocol | `0xa0b86991c...` (USDC Contract) | Ethereum | Etherscan |
| Active Wallet | `0xd8dA6BF2...` (vitalik.eth) | Ethereum | ENS |
| Flagged Scam | `0xff92104f...` | Ethereum + Base | ScamSniffer |
| Multi-Hop Path | `0x66666666...` (synthetic) | Ethereum | Sample Data |

### Using the API Directly

```bash
# Analyze a wallet on Ethereum
curl "http://localhost:8000/report?address=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&chains=ethereum"

# Analyze across multiple chains
curl "http://localhost:8000/report?address=0xff92104ffa62db76aa7fc9ec97442dacfe05e99c&chains=ethereum,base"

# Health check
curl "http://localhost:8000/health"

# List supported chains
curl "http://localhost:8000/chains"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/chains` | GET | List supported chains |
| `/report` | GET | Generate a risk report for an address |

**`/report` Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address` | string | required | Wallet or contract address (0x...) |
| `chains` | string | `ethereum,base` | Comma-separated list of chains to scan |
| `summary` | string | `true` | Include AI-generated narrative summary |

Interactive API docs are available at **http://localhost:8000/docs** (Swagger UI).

---

## 🧪 Testing

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v
```

The test suite covers:
- Scoring engine mathematical invariants (points always sum correctly)
- API endpoint integration tests
- Wallet signal detection logic

There is also a custom evaluation script (`scripts/run_eval.py`) that benchmarks the engine's recall and precision against a blind dataset of known scams with explicit blacklists disabled.

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Cytoscape.js, Lucide Icons |
| Backend | Python, FastAPI, Uvicorn |
| Data Sources | Etherscan V2 API, Blockscout V2 API, Ethereum RPC |
| AI | Google AI Studio (Gemini) |
| Caching | SQLite |
| Testing | Pytest |

---

## 🔒 Security & Trustlessness

**The AI Firewall:** The AI has **absolutely zero control over the risk score**. The scoring engine is 100% deterministic, rule-based Python math. We only use the LLM at the very end of the pipeline as a *translator* — to narrate the finalized JSON report into a plain-English summary paragraph. This means the score can never be hallucinated.

---

## ⚠️ Known Limitations

- **EVM Only** — Currently supports only EVM-compatible chains
- **Off-chain Signatures** — Cannot detect off-chain Permit signature approvals (they emit no logs until execution)
- **History Cap** — APIs paginate up to 10,000 records per address. Very active wallets (e.g., exchange hot wallets) will trigger a "History Truncated" warning

---

## 📄 License

This project was built for a hackathon. See the repository for license details.
