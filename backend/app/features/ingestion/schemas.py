from pydantic import BaseModel, Field

class UnifiedDataPayloadSchema(BaseModel):
    """
    Unified Schema consolidating all ingested data nodes required for 
    downstream Causal Graphs and Monte Carlo simulations.
    All numeric indicators include robust neutral baseline defaults to support
    graceful degradation if specific API points fail.
    """
    # Target Meta
    ticker: str = Field(
        ..., 
        description="The target public company stock ticker symbol (e.g. AMD)"
    )

    # 1. Corporate Health Nodes
    market_cap: float = Field(
        default=0.0, 
        description="Market capitalization in USD"
    )
    beta: float = Field(
        default=1.0, 
        description="Systematic risk coefficient relative to the market (S&P 500)"
    )
    pe_ratio: float = Field(
        default=15.0, 
        description="Price-to-Earnings valuation ratio"
    )
    debt_to_equity: float = Field(
        default=1.0, 
        description="Total Debt to Total Equity ratio (as decimal)"
    )
    historical_volatility: float = Field(
        default=0.25, 
        description="Annualized historical volatility computed over 3 years of daily returns"
    )
    three_year_returns: float = Field(
        default=0.0, 
        description="Cumulative 3-year historical return (as decimal)"
    )
    revenue_growth: float = Field(
        default=0.05, 
        description="Year-over-year revenue growth rate (as decimal)"
    )
    insider_trading_risk_flag: bool = Field(
        default=False, 
        description="Flag indicating suspicious Form 4 insider trading patterns or anomalies"
    )

    # 2. Macroeconomic Nodes
    federal_funds_rate: float = Field(
        default=0.05, 
        description="Effective Federal Funds rate (as decimal)"
    )
    cpi_inflation: float = Field(
        default=0.03, 
        description="Annual Consumer Price Index inflation rate (as decimal)"
    )
    gdp_growth_trend: float = Field(
        default=0.02, 
        description="Real GDP annualized growth rate trend (as decimal)"
    )
    ppi_inflation: float = Field(
        default=0.02,
        description="Producer Price Index for All Commodities inflation rate (as decimal)"
    )
    unemployment_rate: float = Field(
        default=0.04,
        description="Civilian Unemployment Rate (as decimal)"
    )

    # 3. Sentiment & Geopolitical Nodes
    branch_count_risk: float = Field(
        default=0.5, 
        ge=0.0,
        le=1.0,
        description="Geographic/supply chain physical asset exposure score (0.0 to 1.0, 0.5 is neutral)"
    )
    climate_impact_score: float = Field(
        default=0.5, 
        ge=0.0,
        le=1.0,
        description="Climate or environmental disruption risk score (0.0 to 1.0, 0.5 is neutral)"
    )
    public_sentiment_score: float = Field(
        default=0.5, 
        ge=0.0,
        le=1.0,
        description="Public perception/news sentiment score (0.0 to 1.0, 0.5 is neutral)"
    )
    regulatory_pushback_score: float = Field(
        default=0.5, 
        ge=0.0,
        le=1.0,
        description="Regulatory intervention, antitrust, or policy headwind score (0.0 to 1.0, 0.5 is neutral)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AMD",
                "market_cap": 270000000000.0,
                "beta": 1.74,
                "pe_ratio": 45.2,
                "debt_to_equity": 0.05,
                "historical_volatility": 0.42,
                "three_year_returns": 0.85,
                "revenue_growth": 0.12,
                "insider_trading_risk_flag": False,
                "federal_funds_rate": 0.0533,
                "cpi_inflation": 0.032,
                "gdp_growth_trend": 0.025,
                "ppi_inflation": 0.021,
                "unemployment_rate": 0.041,
                "branch_count_risk": 0.1,
                "climate_impact_score": 0.05,
                "public_sentiment_score": 0.35,
                "regulatory_pushback_score": 0.15
            }
        }
