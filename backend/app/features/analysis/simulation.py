import logging
import numpy as np

logger = logging.getLogger("app.features.analysis.simulation")

def run_monte_carlo_simulation(
    metrics: dict,
    inflation_shock_pct: float = 0.0,
    sentiment_shock_pct: float = 0.0,
    n_iterations: int = 10000
) -> dict:
    """
    Runs a 10,000-iteration vectorized NumPy Monte Carlo simulation.
    Applies strict causal graph propagation and confounder correction.
    """
    logger.info(f"Running Monte Carlo simulation with n_iterations={n_iterations}")
    
    np.random.seed(1337)  # Fix seed for reproducible hackathon execution

    # Extract base metrics from payload, applying safe neutral fallbacks
    historical_volatility = float(metrics.get("historical_volatility", 0.25))
    revenue_growth = float(metrics.get("revenue_growth", 0.05))
    debt_to_equity = float(metrics.get("debt_to_equity", 1.0))
    federal_funds_rate = float(metrics.get("federal_funds_rate", 0.05))
    
    base_cpi = float(metrics.get("cpi_inflation", 0.03))
    base_ppi = float(metrics.get("ppi_inflation", 0.02))
    macro_inflation = (base_cpi + base_ppi) / 2.0  # Combined baseline inflation
    
    base_sentiment = float(metrics.get("public_sentiment_score", 0.5))
    # Convert sentiment from 0-1 range to -1.0 to 1.0 range
    market_sentiment = 2.0 * (base_sentiment - 0.5)

    # Apply external user shock inputs
    target_inflation = macro_inflation + inflation_shock_pct
    target_sentiment = market_sentiment + sentiment_shock_pct

    # 1. Generate Exogenous Distributions
    # Inflation volatility scale proportional to historical stock volatility
    inflation_scale = max(0.005, historical_volatility * 0.05)
    
    macro_inflation_samples = np.random.normal(
        loc=target_inflation, 
        scale=inflation_scale, 
        size=n_iterations
    )
    
    # Raw sentiment standard deviation
    raw_sentiment_samples = np.random.normal(
        loc=target_sentiment, 
        scale=0.15, 
        size=n_iterations
    )

    # 2. Apply Confounder Correction
    # Inflation acts as the confounder of both sentiment and revenue growth.
    # Higher inflation negatively dampens public market sentiment:
    sentiment_samples = raw_sentiment_samples - 0.25 * (macro_inflation_samples - 0.02)
    sentiment_samples = np.clip(sentiment_samples, -1.0, 1.0)

    # 3. Propagate Causal Pathways using Structural Equations
    # Revenue Growth = base_revenue_growth - path_coefficient * inflation_deviation
    revenue_growth_samples = (
        revenue_growth 
        - 0.35 * (macro_inflation_samples - 0.02) 
        + np.random.normal(loc=0.0, scale=0.015, size=n_iterations)
    )

    # Debt Service Ratio increases under high inflation via rising baseline rates
    debt_service_ratio_samples = (
        debt_to_equity * (federal_funds_rate + 0.5 * (macro_inflation_samples - 0.02))
        + np.random.normal(loc=0.0, scale=0.01, size=n_iterations)
    )
    debt_service_ratio_samples = np.clip(debt_service_ratio_samples, 0.0, None)

    # 4. Valuation Shock Target Equation
    # Target: Corporate Valuation change percentage
    valuation_change_samples = (
        1.6 * (revenue_growth_samples - 0.05)
        - 0.9 * (debt_service_ratio_samples - 0.1)
        + 0.35 * sentiment_samples
    ) * 100.0  # Convert to percentage

    # Ensure no NaN or Inf values exist in output arrays
    valuation_change_samples = np.nan_to_num(valuation_change_samples, nan=0.0, posinf=50.0, neginf=-50.0)

    # 5. Extract Metrics
    expected_valuation_change_pct = float(np.mean(valuation_change_samples))
    
    conf_90 = np.percentile(valuation_change_samples, [5, 95])
    conf_95 = np.percentile(valuation_change_samples, [2.5, 97.5])
    
    # Calculate probability of drawdown exceeding -15.0%
    risk_of_severe_drawdown_prob = float(np.mean(valuation_change_samples < -15.0))

    # Identify primary causal driver mathematically via relative effect magnitude
    inflation_impact = abs(np.mean(macro_inflation_samples - 0.02) * -0.35 * 1.6)
    sentiment_impact = abs(np.mean(sentiment_samples) * 0.35)
    
    if inflation_impact >= sentiment_impact:
        primary_causal_driver = "Macro_Inflation"
    else:
        primary_causal_driver = "Market_Sentiment"

    return {
        "expected_valuation_change_pct": round(expected_valuation_change_pct, 2),
        "confidence_intervals": {
            "90_pct": [round(conf_90[0], 2), round(conf_90[1], 2)],
            "95_pct": [round(conf_95[0], 2), round(conf_95[1], 2)]
        },
        "risk_of_severe_drawdown_prob": round(risk_of_severe_drawdown_prob, 2),
        "primary_causal_driver": primary_causal_driver
    }
