---
title: Project Plan & Scope
description: High-level architecture, latency budgets, and timeline for the Agentic Decision Intelligence Engine.
---

# Agentic Decision Intelligence Engine - Track 3 (AMD Hackathon)
**Target SLA:** < 4.5 seconds per query (Warm Cache)
**Core Value Prop:** Causal AI + Hardware-Optimized Monte Carlo Simulations. 

---

## 0. Scope Lock (The "Drop It" List)
We are building a bulletproof Minimum Viable Product (MVP). We must demonstrate end-to-end functionality five times consecutively without a crash before adding features.

**ðŸ”´ CUT FROM LIVE DEMO (Mention as "Roadmap" in Pitch):**
* **Live Social Scraping (Nitter/Twitter):** Public instances are unstable and rotate tokens. [cite_start]Do not wire this into a judged demo[cite: 531].
* **LinkedIn Scraping:** Severe Terms of Service (ToS) exposure. [cite_start]Drop it[cite: 325].
* [cite_start]**Live OpenCorporates Calls:** API limits are too aggressive (500/month)[cite: 500]. [cite_start]Use Wikidata alone for mapping[cite: 493].
* **UN Comtrade & Threat Intelligence:** Too complex for a 36-hour sprint. [cite_start]Put it in the slide deck[cite: 558, 568].

---

## 1. Architecture & The Latency Budget
[cite_start]We are using **FastAPI** not just because it's Python, but because of its first-class `asyncio` support and seamless integration with NumPy/Pandas[cite: 191].

### The 5-Second Execution Pipeline:
| Stage | Target Time (Warm) | Target Time (Cold) | Execution Strategy |
| :--- | :--- | :--- | :--- |
| **A. Parallel API Ingestion** | 100-400ms | 1.5 - 2.5s | `asyncio.gather()` for yfinance, SEC, FRED. |
| **B. LLM Structured Extraction** | 0.8 - 1.2s | 1.5 - 4.0s | **Llama 3.1 70B** (via Fireworks AI). [cite_start]Constrain output to strict JSON schema[cite: 396]. |
| **C. Causal Math & Monte Carlo** | < 150ms | 150ms - 300ms | [cite_start]Predefined DoWhy DAG templates [cite: 368] + [cite_start]Vectorized NumPy arrays[cite: 371]. |
| **D. LLM Synthesis & Format** | 0.5 - 1.0s | 0.8 - 1.5s | **Llama 3.1 8B**. [cite_start]Fast, 150-word cap[cite: 397]. |
| **Total Expected Latency** | **~2.5s** | **~5.5s** | *Stream intermediate states (SSE) to mask cold-start latency.* |

---

## 2. Data Ingestion Layer (Tier 1 Only)
Fetch everything concurrently. Wrap synchronous libraries like `yfinance` in `asyncio.to_thread` to prevent blocking the main event loop.

* **yfinance (Market Data):** 3-year returns, volatility, market cap. [cite_start]*Warning: Synchronous, must be threaded*[cite: 191, 194].
* **SEC EDGAR (Fundamentals):** Total assets, debt, liabilities. *Warning: Strict 10 req/sec limit. [cite_start]Must use aggressive `TTLCache`*[cite: 203, 206].
* **FRED API (Macro Data):** Interest rates (FEDFUNDS), 10-year yield (DGS10), CPI (CPIAUCSL). 
* [cite_start]**GDELT (Event Tone):** Use GDELT over raw news APIs because it pre-calculates a tone score (-100 to +100), saving us an expensive LLM sentiment-analysis call[cite: 248, 249].

---

## 3. The LLM Routing & Extraction
* [cite_start]**Validation Policy:** Use `Pydantic` models to enforce the JSON schema[cite: 403]. If Llama 70B hallucinated a bad format, we catch it programmatically.
* **Retry Protocol:** We implement a maximum 2-attempt retry using the `tenacity` library. If it fails twice, we instantly inject a default numeric fallback and flag the synthesis output with a "Low Confidence" warning. We do **not** crash the app.

---

## 4. The Math Engine (DoWhy + Monte Carlo)
Do not dynamically generate Causal Graphs. [cite_start]It takes too long and introduces fatal errors (like cyclic loops)[cite: 367, 368].

1.  **Template Routing:** Hardcode 2-3 standard Directed Acyclic Graphs (DAGs) (e.g., "Interest Rate Hike", "Supply Chain Shock"). [cite_start]Route the user query to the closest template using keyword matching[cite: 368].
2.  [cite_start]**Normalization:** Convert all raw extracted values into percentage-of-baseline before passing them into the Monte Carlo simulation[cite: 413]. 
3.  [cite_start]**Volatility Clamping:** Hardcode a volatility floor (e.g., **2%**) and ceiling (e.g., **50%**) so the Monte Carlo arrays don't collapse into deterministic constants or explode into chaos[cite: 418, 419].
4.  **Hardware Optimization:** Keep the Monte Carlo iteration count fixed (e.g., 2,000 to 10,000) and use entirely vectorized NumPy operations. Do not use loops.

---

## 5. Demo-Day Paranoia (The "Circuit Breaker")
Conference Wi-Fi will fail. The SEC EDGAR API will rate-limit us if another team on the same NAT IP is hitting it. 

* **The Failsafe:** We will pre-record 3 perfect, end-to-end JSON responses (Data + Extraction + Simulation) for 3 specific "canned" queries.
* **Graceful Degradation:** If `asyncio.gather()` times out after 3 seconds, the backend silently flips a switch and serves the pre-recorded snapshot. [cite_start]The judges will never see an HTTP 500 error[cite: 421].

---

## 6. Execution Timeline (The 36-Hour Sprint)
* **Hours 0-2 (Infra):** Register Fireworks AI, FRED, and News API keys. Spin up FastAPI skeleton. 
* **Hours 2-8 (Data):** Wire Tier-1 clients (`yfinance`, EDGAR, FRED) with `asyncio.gather()` and a 60-second `TTLCache`.
* **Hours 8-14 (Extraction):** Write the Llama 70B prompt. Build the Pydantic JSON parser. Test against deliberately malformed data.
* **Hours 14-22 (Math):** Hardcode the Causal DAG templates. Write the vectorized NumPy Monte Carlo script. Implement volatility clamps.
* **Hours 22-26 (Sleep):** Mandatory blackout. Exhausted devs write bad code.
* **Hours 26-32 (Synthesis & UI):** Connect the 8B synthesis model. [cite_start]Add Server-Sent Events (SSE) to stream "Fetching SEC Data..." to the React frontend to mask latency[cite: 400]. Render a static SVG of the DAG.
* **Hours 32-36 (Rehearsal):** Run the canned queries. Disconnect the Wi-Fi intentionally to test the Circuit Breaker. Finalize the pitch. Submit.

---

## Engineering Standards
All code quality, configuration, error handling, logging, and other standards have been moved to [engineering_standards.md](file:///d:/study/amd/engineering_standards.md) to keep this plan concise.
