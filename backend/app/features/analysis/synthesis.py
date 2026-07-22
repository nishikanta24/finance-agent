import logging
from app.shared.llm import synthesizer_llm

logger = logging.getLogger("app.features.analysis.synthesis")

SYSTEM_PROMPT = (
    "You are an elite McKinsey management consultant. Write a highly punchy, 3-4 sentence "
    "boardroom strategic summary based on the provided causal simulation results and company financials.\n"
    "CRITICAL REQUIREMENT: You MUST output your response as a valid JSON object with exactly one key: \"summary\". "
    "Do NOT output any markdown blocks, thoughts, planning, or conversational text. ONLY output raw JSON."
)

async def generate_executive_summary(
    ticker: str,
    sim_results: dict,
    base_metrics: dict
) -> str:
    """
    Calls Llama-3.1-8B-Instruct to compile a strategic executive brief of the simulation results.
    All calls are async-first to keep request streams responsive.
    """
    logger.info(f"Generating boardroom strategic summary for ticker: {ticker}")

    # Extract inputs and outputs
    revenue_growth_pct = round(float(base_metrics.get("revenue_growth", 0.05)) * 100, 2)
    debt_equity = round(float(base_metrics.get("debt_to_equity", 1.0)), 2)
    fed_rate_pct = round(float(base_metrics.get("federal_funds_rate", 0.05)) * 100, 2)
    
    expected_val = sim_results.get("expected_valuation_change_pct", 0.0)
    drawdown_risk_pct = round(float(sim_results.get("risk_of_severe_drawdown_prob", 0.0)) * 100, 2)
    primary_driver = sim_results.get("primary_causal_driver", "Macro_Inflation")

    # Format user context prompt requesting JSON
    user_content = (
        f"Generate the strategic summary for {ticker}.\n\n"
        f"Data:\n"
        f"Ticker: {ticker}\n"
        f"Revenue Growth: {revenue_growth_pct}%\n"
        f"Debt-to-Equity Ratio: {debt_equity}\n"
        f"Fed Funds Rate: {fed_rate_pct}%\n"
        f"Projected Valuation Change: {expected_val}%\n"
        f"Risk of Severe Drawdown: {drawdown_risk_pct}%\n"
        f"Primary Causal Driver: {primary_driver}\n\n"
        f"Output ONLY JSON in this exact format:\n"
        f"{{\n"
        f"  \"summary\": \"Your 3-4 sentence boardroom analysis goes here.\"\n"
        f"}}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    try:
        # Request completion via the synthesizer model wrapper with high tokens for <think> blocks
        summary_text = await synthesizer_llm.generate_chat_completion(
            messages=messages,
            max_tokens=2000
        )
        
        import json
        cleaned_text = summary_text.strip()
        start_idx = cleaned_text.find('{')
        end_idx = cleaned_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            cleaned_text = cleaned_text[start_idx:end_idx+1]
            
        try:
            parsed = json.loads(cleaned_text)
            cleaned_summary = parsed.get("summary", summary_text)
        except json.JSONDecodeError:
            cleaned_summary = summary_text
        
        prefixes_to_strip = [
            "### Actual Output:",
            "Actual Output:",
            "Summary:",
            "Executive Summary:",
            "Strategic Summary:",
            "McKinsey Summary:",
            "Boardroom Strategic Summary:"
        ]
        
        for prefix in prefixes_to_strip:
            if cleaned_summary.lower().startswith(prefix.lower()):
                cleaned_summary = cleaned_summary[len(prefix):].strip()
                
        cleaned_summary = cleaned_summary.strip().strip('"').strip("'").strip()
        logger.info(f"Boardroom summary generated and cleaned successfully for {ticker}.")
        return cleaned_summary

    except Exception as e:
        logger.error(f"Failed to generate LLM boardroom summary: {e}")
        # Return fallback summary text in case of LLM outage
        return (
            f"Valuation outcomes for {ticker} are primarily driven by {primary_driver}. "
            f"Despite external shocks, the company shows an expected valuation change of {expected_val}% "
            f"with a drawdown risk of {drawdown_risk_pct}%. This is supported by its baseline revenue growth of "
            f"{revenue_growth_pct}% and debt-to-equity leverage profile of {debt_equity}."
        )
