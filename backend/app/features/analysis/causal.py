import logging
import pandas as pd
from dowhy import CausalModel

logger = logging.getLogger("app.features.analysis.causal")

# Defined structural DAG representing economic relationships
CAUSAL_GRAPH_GML = """
graph [
    directed 1
    node [ id "Macro_Inflation" label "Macro_Inflation" ]
    node [ id "Market_Sentiment" label "Market_Sentiment" ]
    node [ id "Revenue_Growth" label "Revenue_Growth" ]
    node [ id "Debt_Service_Ratio" label "Debt_Service_Ratio" ]
    node [ id "Corporate_Valuation" label "Corporate_Valuation" ]
    
    edge [ source "Macro_Inflation" target "Revenue_Growth" ]
    edge [ source "Macro_Inflation" target "Debt_Service_Ratio" ]
    edge [ source "Market_Sentiment" target "Corporate_Valuation" ]
    edge [ source "Revenue_Growth" target "Corporate_Valuation" ]
    edge [ source "Debt_Service_Ratio" target "Corporate_Valuation" ]
]
"""

def initialize_causal_model(
    data: pd.DataFrame,
    treatment: str = "Macro_Inflation",
    outcome: str = "Corporate_Valuation"
) -> CausalModel:
    """
    Initializes a DoWhy CausalModel using the strict structural DAG.
    """
    logger.info(f"Initializing DoWhy CausalModel for treatment={treatment} and outcome={outcome}")
    try:
        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            graph=CAUSAL_GRAPH_GML
        )
        return model
    except Exception as e:
        logger.error(f"Failed to initialize DoWhy CausalModel: {e}")
        raise

def create_baseline_dataframe(metrics: dict) -> pd.DataFrame:
    """
    Constructs a synthetic covariance dataset around the baseline company metrics
    so that DoWhy has a populated data object to load.
    """
    # Create 10 baseline historical rows with slight random variation to satisfy DoWhy requirements
    # Shifting metric values to match DAG nomenclature
    import numpy as np
    
    n_samples = 20
    np.random.seed(42)
    
    macro_inf = metrics.get("cpi_inflation", 0.03)
    # Convert sentiment from 0-1 to -1 to 1 range
    mkt_sent = 2.0 * (metrics.get("public_sentiment_score", 0.5) - 0.5)
    rev_growth = metrics.get("revenue_growth", 0.05)
    
    # Calculate baseline Debt Service Ratio based on debt_to_equity and fed funds rate
    fed_rate = metrics.get("federal_funds_rate", 0.05)
    d_e = metrics.get("debt_to_equity", 1.0)
    debt_service = d_e * fed_rate
    
    # Generate variations
    df_dict = {
        "Macro_Inflation": np.random.normal(loc=macro_inf, scale=0.005, size=n_samples),
        "Market_Sentiment": np.random.normal(loc=mkt_sent, scale=0.1, size=n_samples),
    }
    
    # Propagate causal DAG path variation
    df_dict["Revenue_Growth"] = rev_growth - 0.3 * (df_dict["Macro_Inflation"] - macro_inf) + np.random.normal(0, 0.01, n_samples)
    df_dict["Debt_Service_Ratio"] = df_dict["Macro_Inflation"] * d_e + np.random.normal(0, 0.005, n_samples)
    df_dict["Corporate_Valuation"] = (
        100.0 * (1.0 + 1.5 * df_dict["Revenue_Growth"] - 0.8 * df_dict["Debt_Service_Ratio"] + 0.3 * df_dict["Market_Sentiment"])
        + np.random.normal(0, 2.0, n_samples)
    )
    
    return pd.DataFrame(df_dict)
