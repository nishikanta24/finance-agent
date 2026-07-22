# Aethel module layout

This project is a feature-oriented modular monolith. It deliberately keeps one FastAPI service and one React application, so the MVP stays simple while its capabilities remain independently understandable.

## Backend

- `app/features/ingestion`: company, macroeconomic, and news/sentiment collection; its request schema and in-memory cache.
- `app/features/analysis`: SSE scenario endpoint, causal graph, Monte Carlo simulation, and executive synthesis.
- `app/core`: configuration and application-wide runtime concerns.
- `app/shared`: cross-feature integrations, currently the LLM client.

## Frontend

- `src/features/analysis`: query-driven scenario analysis and its visualizations.
- `src/features/market-overview`: market context widgets and their display data.
- `src/shared`: UI primitives and generic utilities.
- `src/app`: application composition only.

The public backend contract remains under `/api/v1/ingestion` and `/api/v1/analytics`, so this refactor does not require client API changes.
