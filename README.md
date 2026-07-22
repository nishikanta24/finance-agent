# Agentic Causal Intelligence & Monte Carlo Risk Engine 📈


---

## 🌟 Origin & Motivation

When evaluating investments in public companies, traditional financial models often focus purely on correlation or static historical metrics. However, investors face two critical questions:
1. **What specific macro & sentiment factors are driving a company's performance, and how do they cause changes in valuation?**
2. **Under external economic shocks (e.g., inflation spikes, negative news sentiment), what is the best-case and worst-case range of potential valuation outcomes?**

Coming from a non-finance background and exploring the frontiers of Artificial Intelligence, this project was built to bridge the gap between **Large Language Models (LLMs)** and **Structural Econometrics**. By marrying LLM-driven news extraction with **DoWhy Causal Graphs** and **Vectorized Monte Carlo Simulations**, this engine transforms unstructured market data into probabilistic risk distributions and boardroom-ready strategic briefs.

---

## 🏗️ Architecture & Core Engine Pipeline

The system operates as a feature-oriented modular engine executing a sub-5-second analysis pipeline:

```
                  ┌─────────────────────────────────────────┐
                  │ 1. Parallel Asynchronous Ingestion      │
                  │    • yfinance (Financials & Beta)       │
                  │    • FRED API (Fed Funds & Inflation)   │
                  │    • GDELT / NewsAPI (News Tone)        │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 2. LLM Risk Vector Extraction           │
                  │    • Llama 3.1 70B / Nemotron-3         │
                  │    • Strict Pydantic Schema Validation  │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 3. Structural Causal DAG & Confounders  │
                  │    • DoWhy CausalModel Validation       │
                  │    • Inflation Confounder Adjustment    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 4. Vectorized Monte Carlo Engine        │
                  │    • 10,000-iteration NumPy Engine      │
                  │    • 90%/95% Confidence Intervals       │
                  │    • Severe Drawdown Probability (>15%) │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 5. Executive Brief & Real-Time SSE Stream │
                  │    • Llama 3.1 8B Boardroom Synthesis   │
                  │    • SSE Stream -> React/TS Dashboard   │
                  └─────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. 🔄 Parallel Asynchronous Ingestion
- Wraps synchronous financial APIs (`yfinance`) inside `asyncio.to_thread` to prevent event loop blocking.
- Concurrently fetches macro indicators (Fed Funds Rate, CPI, PPI from FRED API) and news feeds (GDELT / NewsAPI).
- Implements an **in-memory TTL state cache** enabling sub-second response times for warm follow-up queries.

### 2. 🕸️ Structural Causal Modeling (DoWhy)
- Maps explicit **Cause $\rightarrow$ Effect** Directed Acyclic Graphs (DAGs) rather than naive linear correlations.
- Adjusts for **confounder variables** (e.g., Inflation acting as a mutual confounder dampening both revenue growth and public sentiment).

### 3. 🎲 Vectorized Monte Carlo Risk Engine
- Runs **10,000 randomized iterations** per simulation using high-performance vectorized NumPy operations.
- Outputs probabilistic risk metrics:
  - **Expected Valuation Change (%)**
  - **$90\%$ & $95\%$ Confidence Intervals** (Best-Case vs. Worst-Case Scenarios)
  - **Tail Drawdown Risk Probability** (Probability of $>15\%$ valuation loss)
  - **Primary Causal Driver Identification**

### 4. 📝 Boardroom Strategic Synthesis
- Uses **Llama 3.1 8B / Nemotron-3** to synthesize complex simulation outputs into a 3-4 sentence McKinsey-style boardroom summary.

### 5. ⚡ Real-Time Streaming & Modern Frontend
- Streams progress milestones to the frontend in real time via **Server-Sent Events (SSE)**.
- Built with a React + TypeScript + Tailwind CSS dashboard ([`aethel-dashboard`](./aethel-dashboard)).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend & API** | Python 3.11+, FastAPI, Uvicorn, AsyncIO, Pydantic |
| **Econometrics & Math** | Microsoft DoWhy, NumPy, Pandas, SciPy |
| **AI / LLM Integration** | Fireworks AI, OpenRouter API, Llama 3.1 (70B & 8B), Nemotron-3 |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts |

---

## 🚀 Quick Start & Installation

### Option 1: One-Click Launch (Windows)
Run the automated launcher script from the root directory:
```powershell
.\run_all.bat
```
*(This automatically launches FastAPI on port `8000`, Vite on port `5173`, and opens `http://localhost:5173` in your browser).*

---

### Option 2: Manual Setup

#### 1. Configure Environment Variables
Copy `.env.example` to `.env` in the `backend/` directory and add your API keys:
```ini
FIREWORKS_API_KEY="your_fireworks_api_key"
OPENROUTER_API_KEY="your_openrouter_api_key_optional"
FRED_API_KEY="your_fred_api_key"
NEWS_API_KEY="your_news_api_key"
```

#### 2. Start the Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### 3. Start the Frontend
In a separate terminal:
```powershell
cd aethel-dashboard
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🗺️ Project Roadmap & Extensions

- [ ] **Industry-Specific DAG Templates**: Expand from the universal macro DAG to domain-specific templates (Semiconductors/Tech, Banking/Financials, Retail/Consumer, Real Estate).
- [ ] **Real-Time Insider Trading Anomaly Scanning**: Deeper SEC Form 4 parsing via EDGAR API.
- [ ] **Live Alternative Data Feeds**: Integrating real-time sentiment scoring from social & geopolitical feeds.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
