# TrustTrail

**TrustTrail** is a cross-chain risk analysis engine for wallets and smart contracts. Every risk flag comes with proof (tx hashes and on-chain evidence). It scores addresses based on rule-based heuristics across Ethereum and Base, and uses an LLM solely to generate a plain-English explanation.

## Problem Statement & Features

| Requirement | TrustTrail Feature |
| --- | --- |
| Cross-chain risk report | Fetches history from Ethereum (Etherscan) and Base (Blockscout). |
| Findings have evidence & rules | Every signal contains evidence (tx hashes) and ule strings. |
| Transparent, rule-based scoring | scoring.py assigns static weights capped at 100, no LLM scoring. |
| LLM plain-English summary | Google AI Studio model parses findings and outputs a short summary. |

## Architecture

`mermaid
flowchart TD
    Client[React Frontend] -->|GET /report| API[FastAPI Backend]
    API --> Cache[(SQLite Cache)]
    API --> Analyze[Analyze Engine]
    Analyze --> WS[Wallet Signals]
    Analyze --> CS[Contract Signals]
    Analyze --> LLM[Google AI Studio]
    WS --> Etherscan[Etherscan API V2]
    WS --> Blockscout[Blockscout API V2]
    CS --> RPC[Ethereum & Base RPC]
`

## Setup & Environment

1. python -m venv venv and activate it.
2. pip install -r requirements.txt
3. cd frontend && npm install
4. Copy .env.example to .env and fill:
   - ETHERSCAN_API_KEY: For Ethereum/Arbitrum V2 history.
   - LLM_API_KEY: For AI summary generation.
   - LLM_BASE_URL: https://generativelanguage.googleapis.com/v1beta/openai/
   - LLM_MODEL: gemini-3.8-flash (or your deployed model)
   - OFFLINE: Set to 1 to only serve pre-warmed cache reports.
   - RPC_URL_1, RPC_URL_8453: Your RPC endpoints.

## Running

Start both frontend and backend using:
`ash
python scripts/run_dev.py
`
Open http://localhost:5173.

## Testing & Evaluation

- **Tests**: pytest
- **Eval**: python -m backend.eval.run_eval --limit 40. Evaluates precision/recall on a held-out scam dataset with explicit list lookups disabled.

## Known Limitations

- **EVM Only**: Only supports EVM-compatible chains.
- **Off-chain Signatures**: Cannot detect off-chain Permit signature approvals.
- **History Cap**: API paginates up to 10,000 records per address.
- **Base History**: Uses Blockscout (as Etherscan V2 requires a paid plan for Base).
- **LLM Scope**: The LLM is restricted to narration and cannot alter the risk score.
- **List Reliance**: Some signals heavily depend on the ScamSniffer database.

## Troubleshooting

- **No summary generated**: Check LLM_API_KEY. It will safely fall back to a deterministic string if it fails.
- **Rate limits**: cache.py automatically spaces requests by 0.25s and retries 5xx/429 errors.
