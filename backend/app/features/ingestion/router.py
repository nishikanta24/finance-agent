import time
import logging
import asyncio
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.features.ingestion.schemas import UnifiedDataPayloadSchema
from app.features.ingestion.service import (
    fetch_corporate_data,
    fetch_macro_data,
    fetch_sentiment_and_alternative_data
)
from app.features.ingestion.cache import (
    has_data,
    get_company_data,
    save_company_data
)

logger = logging.getLogger("app.api.v1.ingestion")

router = APIRouter(
    prefix="/ingestion",
    tags=["data-ingestion"]
)

class IngestionRequest(BaseModel):
    ticker: str = Field(..., description="Target company ticker symbol (e.g. AMD)", example="AMD")

@router.post(
    "/fetch", 
    response_model=UnifiedDataPayloadSchema,
    status_code=status.HTTP_200_OK,
    summary="Fetch and unify corporate, macro, and sentiment risk indicators concurrently"
)
async def fetch_and_unify_data(request: IngestionRequest):
    """
    POST endpoint to ingest all data streams for a given ticker.
    Concurrently runs Corporate Health (yfinance), Macroeconomic (FRED), and News Sentiment (GDELT/Llama) tasks.
    Checks the in-memory cache first to support < 1s follow-up queries (Warm Cache).
    """
    ticker = request.ticker.upper().strip()
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker symbol must not be empty."
        )

    # Check state cache first
    if has_data(ticker):
        cached_payload = get_company_data(ticker)
        if cached_payload is not None:
            logger.info(f"Direct warm cache serve completed for ticker: {ticker}")
            return UnifiedDataPayloadSchema(**cached_payload)

    logger.info(f"Incoming data ingestion request triggered for ticker: {ticker}")
    overall_start = time.perf_counter()

    # Define wrapper functions with latency tracking
    async def track_corporate():
        s = time.perf_counter()
        res = await fetch_corporate_data(ticker)
        e = time.perf_counter()
        logger.info(f"Corporate health data ingested in {e - s:.4f} seconds")
        return res

    async def track_macro():
        s = time.perf_counter()
        res = await fetch_macro_data()
        e = time.perf_counter()
        logger.info(f"Macroeconomic data ingested in {e - s:.4f} seconds")
        return res

    async def track_sentiment():
        s = time.perf_counter()
        res = await fetch_sentiment_and_alternative_data(ticker)
        e = time.perf_counter()
        logger.info(f"Geopolitical/Sentiment data ingested in {e - s:.4f} seconds")
        return res

    # Coordinate tasks concurrently using asyncio.gather
    try:
        corporate_data, macro_data, sentiment_data = await asyncio.gather(
            track_corporate(),
            track_macro(),
            track_sentiment()
        )
    except Exception as e:
        logger.critical(f"Critical failure during data ingestion orchestration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion orchestration failed: {str(e)}"
        )

    # Merge dictionaries
    consolidated_payload = {
        "ticker": ticker,
        **corporate_data,
        **macro_data,
        **sentiment_data
    }
    
    # Insider risk is flagged if detected via Form 4 filings OR news analysis
    consolidated_payload["insider_trading_risk_flag"] = (
        corporate_data.get("insider_trading_risk_flag", False) or 
        sentiment_data.get("insider_trading_risk_flag", False)
    )

    # Prioritize Yahoo ESG data for climate and regulatory pushback if it was successfully fetched (not default 0.5)
    if corporate_data.get("climate_impact_score", 0.5) != 0.5:
        consolidated_payload["climate_impact_score"] = corporate_data["climate_impact_score"]
    if corporate_data.get("regulatory_pushback_score", 0.5) != 0.5:
        consolidated_payload["regulatory_pushback_score"] = corporate_data["regulatory_pushback_score"]

    overall_end = time.perf_counter()
    logger.info(f"Total pipeline ingestion duration: {overall_end - overall_start:.4f} seconds")

    # Validate output structure using the Unified Pydantic Schema
    validated_payload = UnifiedDataPayloadSchema(**consolidated_payload)
    
    # Cache payload for fast follow-up retrieves
    save_company_data(ticker, validated_payload.dict())
    
    return validated_payload
