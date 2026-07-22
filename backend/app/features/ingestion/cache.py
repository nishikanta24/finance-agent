import logging
from typing import Dict, Any

logger = logging.getLogger("app.features.ingestion.cache")

# A global dictionary serving as the in-memory cache for ingestion payloads
_SESSION_CACHE: Dict[str, Dict[str, Any]] = {}

def save_company_data(ticker: str, payload: dict[str, Any]) -> None:
    """
    Saves the extracted and validated payload dictionary to memory.
    """
    cleaned_ticker = ticker.upper().strip()
    _SESSION_CACHE[cleaned_ticker] = payload
    logger.info(f"Successfully cached data payload for ticker: {cleaned_ticker}")

def get_company_data(ticker: str) -> dict[str, Any] | None:
    """
    Retrieves the payload if it exists, otherwise returns None.
    """
    cleaned_ticker = ticker.upper().strip()
    payload = _SESSION_CACHE.get(cleaned_ticker)
    if payload:
        logger.info(f"Cache HIT for ticker: {cleaned_ticker}")
    else:
        logger.info(f"Cache MISS for ticker: {cleaned_ticker}")
    return payload

def has_data(ticker: str) -> bool:
    """
    Checks if a ticker's payload is cached in memory.
    """
    cleaned_ticker = ticker.upper().strip()
    return cleaned_ticker in _SESSION_CACHE

def clear_cache() -> None:
    """
    Clears all cached company payloads.
    """
    _SESSION_CACHE.clear()
    logger.info("Cleared all cached session payloads.")
