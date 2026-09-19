# TrustTrail: The Pitch Playbook

This is your master guide for presenting TrustTrail. Read this a few times to get comfortable, and you will be completely bulletproof when the judges ask questions.

---

## 1. The Hook (Your Opening)

**"Hi, I'm Chris. Today I'm presenting TrustTrail.**

If you look at Web3 security today, it's completely fragmented. If you want to know if a smart contract or a wallet is safe, you either stare at a block explorer which is just a wall of raw hex data, or you pay thousands of dollars for enterprise forensics tools. 

I built TrustTrail to democratize cross-chain security. It’s an engine that takes any wallet or contract address, scans its entire interaction history across multiple blockchains, and generates an instant, human-readable risk report. 

And our core philosophy is: **Every risk flag comes with proof.** We don't just say 'High Risk'—we link you to the exact transaction hashes that prove it."

---

## 2. Walking Through the UI Demos

*As you talk, click through the demo buttons at the top of the UI.*

### Demo 1: Safe Protocol (USDC)
* **What to click:** `Safe Protocol (USDC)`
* **What to say:** "Let's start with a safe, famous contract: USDC. TrustTrail doesn't just blindly whitelist big names. It actually inspects the contract structure. Here, it correctly identifies that USDC is an **Upgradeable Proxy**. This means the admins can technically change the code at any time. It flags this as a structural risk, but because the contract's interaction history is otherwise perfectly clean, it gets a highly trusted score of 0."

### Demo 2: Active Wallet (Vitalik.eth)
* **What to click:** `Active Wallet (Medium Risk)`
* **What to say:** "Now let's look at a highly active user—this is actually Vitalik Buterin's public wallet. The engine pulls 10,000 transactions and maps his counterparties. Even though it's a famous wallet, TrustTrail flags that he has left multiple **Unlimited Token Approvals** open on random DeFi contracts over the years. This shows how our engine catches the subtle, chronic security hygiene issues that lead to retail users getting drained."

### Demo 3: Flagged Scam
* **What to click:** `Flagged Scam`
* **What to say:** "Of course, we also integrate with explicit threat-intel databases. This is a known phishing wallet. The system immediately red-flags it with a 100/100 score, isolating the exact transactions where the malicious activity occurred."

### Demo 4: The Boss Level
* **What to click:** `BOSS: Lazarus Laundering Ring`
* **What to say:** "Finally, I want to show you the power of our Interaction Graph. This simulates a massive cybercriminal hub. The Cytoscape physics engine dynamically maps out a web of 80 nodes where 20 exploited victims funnel funds into a central hub, which then systematically wash-trades the funds across 50 different mixer contracts. It visualizes the money laundering topology instantly."

---

## 3. How the Tech Works (Backend Architecture)

If they ask how you built it, here is your stack:

* **The Engine (Python/FastAPI):** An asynchronous backend that coordinates fetching data, running heuristics, scoring, and AI narration.
* **The Data Layer:** It is truly cross-chain. It queries **Etherscan V2** for Ethereum and **Blockscout V2** for Base. 
* **The Cache:** To survive the hackathon and bypass strict free-tier API limits, I wrote a custom SQLite caching layer. It spaces every API request exactly 0.25 seconds apart and gracefully retries if it hits a rate limit.
* **The Heuristics:** The rules are pure Python math. We don't just rely on APIs. For example, to detect if a contract is a proxy, we use an RPC node to literally call `eth_getStorageAt` and check the EIP-1967 memory slots ourselves.
* **The Frontend:** React, Vite, and Tailwind CSS v4, utilizing Cytoscape.js for the dynamic physics-based interaction graph.

---

## 4. The Role of AI (Crucial Point!)

*Judges love asking about AI hallucinations in security. Use this to impress them:*

**Judge:** "Security is critical. How do you prevent the AI from hallucinating a false risk score?"

**Your Answer:** "That's exactly why I strictly firewalled the AI. **The LLM has absolutely zero control over the risk score.** Our scoring is 100% deterministic and rule-based in Python. We only use the LLM (Google AI Studio) at the very end of the pipeline as a *translator*. We feed it our finalized JSON report, and it simply narrates our evidence into a plain-English paragraph for non-technical users. If the LLM breaks or hallucinates, the hard math of the risk score remains totally unaffected."

---

## 5. Rapid-Fire Q&A (Be Prepared)

**Q: How do you handle massive exchange wallets with millions of transactions?**
**A:** "We paginate up to the latest 10,000 interactions per address. For 99% of retail users and standard protocols, this captures their entire history. For Binance hot wallets, the system detects the cap and explicitly flags `Warnings: History Truncated`, ensuring the user knows the graph is partial."

**Q: Are you just relying on a blacklist to catch scams?**
**A:** "No. We do use the ScamSniffer database for explicit blocks, but I actually wrote an evaluation script (`run_eval.py`) that disables the blacklist entirely and tests our engine against a blind dataset. Even without the blacklist, we catch scams by looking at structural heuristics—like fresh wallets with zero history suddenly deploying unverified, proxy-pattern contracts."

**Q: Can you detect off-chain phishing signatures like `Permit2`?**
**A:** "Currently, we scan strictly on-chain data (EVM logs and state). Off-chain signatures are a known limitation because they don't emit logs until they are executed on-chain. In the future, we could integrate with a mempool scanner to catch those."

**Q: Why did you use Blockscout for Base instead of Etherscan?**
**A:** "Etherscan V2 requires a paid Pro plan to access Base network data. To keep this project completely free and open-source, I designed the data layer to be modular. It seamlessly normalizes the schema differences between Etherscan and Blockscout so the analysis engine doesn't even know the difference."
