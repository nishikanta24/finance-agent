import os
import math
import json
import time
import logging
import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from app.core.settings import settings
from app.shared.llm import extractor_llm

logger = logging.getLogger("app.features.ingestion.service")

# =====================================================================
# 1. Corporate Data Ingestion (yfinance wrapper)
# =====================================================================

def _sync_fetch_yfinance(ticker: str) -> dict:
    """
    Synchronous yfinance execution block. Run inside an executor thread.
    """
    logger.info(f"Initiating yfinance API call for {ticker}")
    t = yf.Ticker(ticker)
    
    # 1. Get fundamental info
    info = t.info
    if not info:
        logger.warning(f"No fundamental info found for {ticker}")
        info = {}
        
    market_cap = float(info.get("marketCap", 0.0))
    beta = float(info.get("beta", 1.0))
    pe_ratio = float(info.get("trailingPE", info.get("forwardPE", 15.0)))
    
    # yfinance returns debtToEquity in percentage (e.g. 5.5 means 0.055, or 102.5 means 1.025)
    debt_equity_raw = info.get("debtToEquity", None)
    if debt_equity_raw is not None:
        debt_to_equity = float(debt_equity_raw) / 100.0 if float(debt_equity_raw) > 5.0 else float(debt_equity_raw)
    else:
        debt_to_equity = 1.0
        
    revenue_growth = float(info.get("revenueGrowth", 0.05))

    # --- 10-K Fallback Hacks (Financials / Balance Sheet) ---
    # Fallback for debt_to_equity if missing or default
    if debt_to_equity == 1.0 or debt_to_equity == 0.0:
        try:
            bs = t.balance_sheet
            if bs is not None and not bs.empty:
                total_debt = None
                total_equity = None
                for label in bs.index:
                    lbl_lower = str(label).lower()
                    if 'total debt' in lbl_lower or 'long term debt' in lbl_lower:
                        val = bs.loc[label].iloc[0]
                        if not pd.isna(val) and float(val) > 0:
                            total_debt = float(val)
                    if 'stockholders equity' in lbl_lower or 'total equity' in lbl_lower:
                        val = bs.loc[label].iloc[0]
                        if not pd.isna(val) and float(val) > 0:
                            total_equity = float(val)
                if total_debt is not None and total_equity is not None and total_equity > 0:
                    debt_to_equity = total_debt / total_equity
                    logger.info(f"Fallback 10-K: Calculated debt_to_equity from balance_sheet: {debt_to_equity:.4f}")
        except Exception as ex:
            logger.warning(f"Could not compute 10-K balance_sheet fallback for debt_to_equity: {ex}")

    # Fallback for revenue_growth if missing or default
    if revenue_growth == 0.05 or revenue_growth == 0.0:
        try:
            fin = t.financials
            if fin is not None and not fin.empty:
                for label in fin.index:
                    lbl_lower = str(label).lower()
                    if 'total revenue' in lbl_lower or 'revenue' in lbl_lower:
                        val_latest = fin.loc[label].iloc[0]
                        val_prev = fin.loc[label].iloc[1]
                        if not pd.isna(val_latest) and not pd.isna(val_prev) and val_prev > 0:
                            revenue_growth = (float(val_latest) / float(val_prev)) - 1.0
                            logger.info(f"Fallback 10-K: Calculated revenue_growth from financials: {revenue_growth:.4f}")
                            break
        except Exception as ex:
            logger.warning(f"Could not compute 10-K financials fallback for revenue_growth: {ex}")

    # --- Form 4 Insider Trading Scanning ---
    insider_trading_risk_flag = False
    
    # Method A: Check insider purchases summary (last 6 months)
    try:
        insider_purchases = t.insider_purchases
        if insider_purchases is not None and not insider_purchases.empty:
            for idx, row in insider_purchases.iterrows():
                idx_str = str(idx).lower()
                if "net" in idx_str or "purchased (sold)" in idx_str:
                    shares_val = row.get("Shares", 0.0)
                    if float(shares_val) < -500000:
                        insider_trading_risk_flag = True
                        logger.warning(f"Form 4: Flagged insider trading risk for {ticker}: Net shares sold = {shares_val}")
    except Exception as ex:
        logger.warning(f"Form 4: Failed to check insider purchases: {ex}")

    # Method B: Check detailed insider transactions list
    try:
        if not insider_trading_risk_flag:
            insider_df = t.insider_transactions
            if insider_df is not None and not insider_df.empty:
                text_cols = [col for col in insider_df.columns if col.lower() in ["text", "transaction", "transactiontype"]]
                shares_cols = [col for col in insider_df.columns if col.lower() == "shares"]
                if shares_cols:
                    shares_col = shares_cols[0]
                    net_shares = 0.0
                    for idx, row in insider_df.iterrows():
                        try:
                            shares_num = float(row[shares_col])
                        except (ValueError, TypeError):
                            shares_num = 0.0
                        is_sale = False
                        for col in text_cols:
                            val_str = str(row[col]).lower()
                            if "sale" in val_str or "sell" in val_str or "disposition" in val_str:
                                is_sale = True
                                break
                            elif "purchase" in val_str or "buy" in val_str or "acquisition" in val_str:
                                is_sale = False
                                break
                        if is_sale:
                            net_shares -= shares_num
                        else:
                            net_shares += shares_num
                    if net_shares < -500000:
                        insider_trading_risk_flag = True
                        logger.warning(f"Form 4: Flagged insider trading risk for {ticker}: Cumulative transactions = {net_shares} shares")
    except Exception as ex:
        logger.warning(f"Form 4: Failed to check detailed transactions: {ex}")

    # --- ESG Sustainability Data Ingestion ---
    climate_impact_score = 0.5
    regulatory_pushback_score = 0.5
    try:
        esg_data = t.sustainability
        if esg_data is not None and not esg_data.empty:
            for idx, row in esg_data.iterrows():
                idx_lower = str(idx).lower()
                val = row.iloc[0]
                if not pd.isna(val):
                    if 'environmentscore' in idx_lower:
                        climate_impact_score = max(0.0, min(1.0, float(val) / 100.0))
                    elif 'governancescore' in idx_lower:
                        regulatory_pushback_score = max(0.0, min(1.0, float(val) / 100.0))
            logger.info(f"Loaded yfinance ESG data: climate={climate_impact_score:.4f}, regulatory={regulatory_pushback_score:.4f}")
    except Exception as ex:
        logger.warning(f"Could not fetch yfinance ESG data: {ex}")

    # 2. Get 3-year historical time-series for CAGR and volatility
    logger.info(f"Fetching 3-year historical Close prices for {ticker}")
    history = t.history(period="3y")
    
    historical_volatility = 0.25  # default baseline
    three_year_returns = 0.0      # default baseline
    
    if not history.empty and len(history) > 30:
        close_prices = history["Close"]
        
        # Volatility: Standard deviation of daily pct changes, annualized
        daily_returns = close_prices.pct_change().dropna()
        daily_std = daily_returns.std()
        if not math.isnan(daily_std):
            historical_volatility = float(daily_std * math.sqrt(252))
            
        # CAGR: (Last_Close / First_Close) ** (1/3) - 1
        first_price = close_prices.iloc[0]
        last_price = close_prices.iloc[-1]
        if first_price > 0 and last_price > 0:
            three_year_returns = float((last_price / first_price) ** (1.0 / 3.0) - 1.0)
            
    logger.info(f"Completed yfinance statistics computation for {ticker}")
    return {
        "market_cap": market_cap,
        "beta": beta,
        "pe_ratio": pe_ratio,
        "debt_to_equity": debt_to_equity,
        "historical_volatility": historical_volatility,
        "three_year_returns": three_year_returns,
        "revenue_growth": revenue_growth,
        "insider_trading_risk_flag": insider_trading_risk_flag,
        "climate_impact_score": climate_impact_score,
        "regulatory_pushback_score": regulatory_pushback_score
    }

async def fetch_corporate_data(ticker: str) -> dict:
    """
    Asynchronously executes corporate financial ingestion in an executor thread.
    Gracefully falls back to baseline values if ticker is not found or API fails.
    """
    baseline = {
        "market_cap": 0.0,
        "beta": 1.0,
        "pe_ratio": 15.0,
        "debt_to_equity": 1.0,
        "historical_volatility": 0.25,
        "three_year_returns": 0.0,
        "revenue_growth": 0.05,
        "insider_trading_risk_flag": False,
        "climate_impact_score": 0.5,
        "regulatory_pushback_score": 0.5
    }
    start_time = time.perf_counter()
    try:
        # Wrap the synchronous blocker in a thread pool
        data = await asyncio.to_thread(_sync_fetch_yfinance, ticker)
        data["yfinance_latency_seconds"] = time.perf_counter() - start_time
        return data
    except Exception as e:
        logger.error(f"yfinance ingestion failed for {ticker}. Error: {e}. Falling back to baseline.")
        baseline["yfinance_latency_seconds"] = time.perf_counter() - start_time
        return baseline


# =====================================================================
# 2. Macroeconomic Data Ingestion (FRED API wrapper)
# =====================================================================

async def fetch_macro_data() -> dict:
    """
    Fetches Federal Funds Rate, CPI (for Inflation calculation), Real GDP,
    PPI, and Unemployment Rate from the FRED API. Degrades gracefully to baselines.
    """
    # Neutral macroeconomic baseline
    baseline = {
        "federal_funds_rate": 0.0525,
        "cpi_inflation": 0.03,
        "gdp_growth_trend": 0.02,
        "ppi_inflation": 0.02,
        "unemployment_rate": 0.04
    }
    
    start_time = time.perf_counter()
    api_key = settings.FRED_API_KEY
    if not api_key:
        logger.warning("FRED_API_KEY is not defined in settings. Using macro baseline defaults.")
        baseline["fred_latency_seconds"] = time.perf_counter() - start_time
        return baseline

    logger.info("Initiating FRED macroeconomic API ingestion")
    
    async def fetch_series(session: aiohttp.ClientSession, series_id: str, limit: int = 15) -> list:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }
        async with session.get(url, params=params, timeout=5.0) as response:
            if response.status != 200:
                logger.error(f"FRED API returned HTTP {response.status} for series {series_id}")
                return []
            res_json = await response.json()
            return res_json.get("observations", [])

    try:
        async with aiohttp.ClientSession() as session:
            # Gather FEDFUNDS, CPIAUCSL, GDPC1, PPIACO, and UNRATE concurrently
            fed_task = fetch_series(session, "FEDFUNDS", limit=5)
            cpi_task = fetch_series(session, "CPIAUCSL", limit=20)
            gdp_task = fetch_series(session, "GDPC1", limit=10)
            ppi_task = fetch_series(session, "PPIACO", limit=20)
            unrate_task = fetch_series(session, "UNRATE", limit=5)
            
            fed_obs, cpi_obs, gdp_obs, ppi_obs, unrate_obs = await asyncio.gather(
                fed_task, cpi_task, gdp_task, ppi_task, unrate_task
            )
            
            macro_data = baseline.copy()
            
            # 1. Calculate Federal Funds Rate (divide percent value by 100)
            if fed_obs:
                latest_fed_val = float(fed_obs[0]["value"])
                macro_data["federal_funds_rate"] = latest_fed_val / 100.0
                
            # 2. Calculate CPI inflation: YoY rate = (CPI_latest / CPI_12_months_ago) - 1
            # Note: Observations are monthly, sorted desc. Latest is index 0, 12 months ago is index 12.
            if len(cpi_obs) >= 13:
                latest_cpi = float(cpi_obs[0]["value"])
                prior_cpi = float(cpi_obs[12]["value"])
                if prior_cpi > 0:
                    macro_data["cpi_inflation"] = (latest_cpi / prior_cpi) - 1.0
                    
            # 3. Calculate Real GDP growth trend: YoY rate = (GDP_latest / GDP_4_quarters_ago) - 1
            # Note: Observations are quarterly, sorted desc. Latest is index 0, 1 year ago is index 4.
            if len(gdp_obs) >= 5:
                latest_gdp = float(gdp_obs[0]["value"])
                prior_gdp = float(gdp_obs[4]["value"])
                if prior_gdp > 0:
                    macro_data["gdp_growth_trend"] = (latest_gdp / prior_gdp) - 1.0

            # 4. Calculate PPI inflation: YoY rate = (PPI_latest / PPI_12_months_ago) - 1
            if len(ppi_obs) >= 13:
                latest_ppi = float(ppi_obs[0]["value"])
                prior_ppi = float(ppi_obs[12]["value"])
                if prior_ppi > 0:
                    macro_data["ppi_inflation"] = (latest_ppi / prior_ppi) - 1.0

            # 5. Calculate Unemployment Rate (divide percent value by 100)
            if unrate_obs:
                latest_unrate = float(unrate_obs[0]["value"])
                macro_data["unemployment_rate"] = latest_unrate / 100.0
            
            logger.info("Successfully fetched macro data from FRED API")
            macro_data["fred_latency_seconds"] = time.perf_counter() - start_time
            return macro_data
            
    except Exception as e:
        logger.error(f"Error during FRED macro ingestion: {e}. Falling back to baseline.")
        baseline["fred_latency_seconds"] = time.perf_counter() - start_time
        return baseline


# =====================================================================
# 3. Alternative & Sentiment Ingestion (GDELT / NewsAPI + Llama Extraction)
# =====================================================================

async def _fetch_raw_news(ticker: str) -> str:
    """
    Fetches raw news headlines from GDELT Doc API (requires no key).
    Falls back to NewsAPI if news key is provided.
    """
    logger.info(f"Fetching raw news feeds for {ticker}")
    news_text = ""
    
    # 1. Try public GDELT Doc API (No Key)
    gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    gdelt_params = {
        "format": "json",
        "query": f'"{ticker}"',
        "mode": "ArtList",
        "maxrecords": "10"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(gdelt_url, params=gdelt_params, timeout=5.0) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    titles = [art.get("title", "") for art in articles if art.get("title")]
                    if titles:
                        news_text = " | ".join(titles)
                        logger.info(f"Ingested {len(titles)} articles from GDELT for {ticker}")
                        return news_text
    except Exception as e:
        logger.warning(f"GDELT Doc API call failed: {e}. Trying NewsAPI as fallback.")

    # 2. Try NewsAPI if key is available
    if settings.NEWS_API_KEY:
        news_url = "https://newsapi.org/v2/everything"
        news_params = {
            "q": ticker,
            "pageSize": "10",
            "apiKey": settings.NEWS_API_KEY
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(news_url, params=news_params, timeout=5.0) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("articles", [])
                        strings = []
                        for art in articles:
                            title = art.get("title", "")
                            desc = art.get("description", "")
                            strings.append(f"{title}: {desc}")
                        if strings:
                            news_text = " | ".join(strings)
                            logger.info(f"Ingested {len(strings)} articles from NewsAPI for {ticker}")
                            return news_text
        except Exception as e:
            logger.error(f"NewsAPI call failed: {e}")
            
    return news_text

async def fetch_sentiment_and_alternative_data(ticker: str) -> dict:
    """
    Orchestrates the GDELT/NewsAPI feed extraction and routes to Llama-3.1-70B
    for structured risk score extraction.
    """
    baseline = {
        "branch_count_risk": 0.5,
        "climate_impact_score": 0.5,
        "public_sentiment_score": 0.5,
        "regulatory_pushback_score": 0.5,
        "insider_trading_risk_flag": False
    }
    
    # 1. Fetch raw news (GDELT)
    gdelt_start = time.perf_counter()
    raw_news = await _fetch_raw_news(ticker)
    gdelt_duration = time.perf_counter() - gdelt_start
    
    # If no news found, load default context
    if not raw_news.strip():
        logger.warning(f"No recent news found for {ticker}. Injecting neutral context.")
        raw_news = (
            f"Overall operational status remains within standard parameters for ticker {ticker}. "
            "No major regulatory actions, geographical branch disruptions, climate exposures, or "
            "insider trading anomalies have been flagged in recent reports."
        )

    # 2. Load prompt template from file
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "prompts",
        "sentiment_extraction.txt"
    )
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    except Exception as e:
        logger.error(f"Failed to load prompt template from {prompt_path}: {e}")
        baseline["gdelt_latency_seconds"] = gdelt_duration
        baseline["extraction_llm_latency_seconds"] = 0.0
        return baseline

    # Format the prompt
    prompt = prompt_template.format(ticker=ticker, text=raw_news)
    
    messages = [
        {"role": "system", "content": "You are a precise JSON risk score extractor. Never output text outside of the requested JSON schema."},
        {"role": "user", "content": prompt}
    ]

    logger.info(f"Routing structured extraction to extractor_llm (70B) for {ticker}")
    
    llm_start = time.perf_counter()
    try:
        # Call the extractor LLM with a high token limit to allow <think> blocks
        llm_response = await extractor_llm.generate_chat_completion(
            messages=messages,
            max_tokens=2000
        )
        llm_duration = time.perf_counter() - llm_start
        
        # Robust JSON extraction to bypass <think> tags or markdown
        cleaned_response = llm_response.strip()
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            cleaned_response = cleaned_response[start_idx:end_idx+1]
        
        # Parse JSON
        result = json.loads(cleaned_response)
        
        # Clean type safety constraints
        validated_data = {
            "branch_count_risk": max(0.0, min(1.0, float(result.get("branch_count_risk", 0.5)))),
            "climate_impact_score": max(0.0, min(1.0, float(result.get("climate_impact_score", 0.5)))),
            "public_sentiment_score": max(0.0, min(1.0, float(result.get("public_sentiment_score", 0.5)))),
            "regulatory_pushback_score": max(0.0, min(1.0, float(result.get("regulatory_pushback_score", 0.5)))),
            "insider_trading_risk_flag": bool(result.get("insider_trading_risk_flag", False)),
            "gdelt_latency_seconds": gdelt_duration,
            "extraction_llm_latency_seconds": llm_duration
        }
        logger.info(f"Structured sentiment extraction completed for {ticker}")
        return validated_data

    except Exception as e:
        logger.error(f"LLM sentiment extraction failed for {ticker}. Error: {e}. Falling back to baseline.")
        llm_duration = time.perf_counter() - llm_start
        baseline["gdelt_latency_seconds"] = gdelt_duration
        baseline["extraction_llm_latency_seconds"] = llm_duration
        return baseline
