---
title: Engineering Standards & Guidelines
description: Mandatory standards for code quality, async handling, configuration, logging, type-safety, and test coverage.
---

# Engineering Standards (Non-Negotiable)

These standards apply even in a hackathon. The goal is to build an MVP that is not only functional but also clean, maintainable, debuggable, and easy to extend after the competition. Prioritize readability and reliability alongside speed.

---

## Project Structure

Maintain a clean, modular architecture with clear separation of concerns.

- Never place all logic inside `main.py`.
- Separate API routes, business logic, data ingestion, LLM services, simulation engine, caching, configuration, prompts, models, and utilities into their own modules.
- Every module should have a **single responsibility**.
- Avoid circular imports.
- Keep files focused and reasonably small.
- Prefer composition over tightly coupled code.
- Organize the codebase so a new developer can understand the project structure within a few minutes.

Example directory structure:

```text
backend/
â”‚
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ api/
â”‚   â”œâ”€â”€ services/
â”‚   â”œâ”€â”€ ingestion/
â”‚   â”œâ”€â”€ llm/
â”‚   â”œâ”€â”€ simulation/
â”‚   â”œâ”€â”€ cache/
â”‚   â”œâ”€â”€ prompts/
â”‚   â”œâ”€â”€ models/
â”‚   â”œâ”€â”€ config/
â”‚   â”œâ”€â”€ utils/
â”‚   â””â”€â”€ main.py
â”‚
â”œâ”€â”€ tests/
â”œâ”€â”€ data/
â”œâ”€â”€ scripts/
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

---

## Configuration Management

Never hardcode configuration values.

- Store API keys inside a `.env` file.
- Load configuration through a dedicated configuration module.
- Centralize configurable values such as:
  - API endpoints
  - timeout values
  - retry counts
  - cache TTL
  - Monte Carlo iterations
  - volatility limits
  - model names
  - feature flags

Configuration should never be scattered throughout the codebase.

---

## Logging

Do **not** rely on random `print()` statements for debugging.

Use Python's built-in `logging` module consistently throughout the project.

Log important execution stages, including:

```text
INFO     Starting request...
INFO     Fetching SEC data...
INFO     Fetching FRED data...
INFO     Running Monte Carlo...
INFO     LLM extraction completed.
WARNING  SEC API timeout.
WARNING  Cache miss.
ERROR    Fireworks API failed.
```

Also log execution time for major pipeline stages:

```text
SEC fetch completed in 182 ms
LLM extraction completed in 931 ms
Monte Carlo completed in 43 ms
Total request latency: 2.41 s
```

Good logs significantly reduce debugging time during the demo.

---

## Error Handling

Never allow uncaught exceptions to crash the backend.

Every external dependency should include:

- timeout
- retry
- graceful fallback
- meaningful logging

If one data source fails, continue with partial data whenever possible instead of failing the entire request.

---

## Type Safety

Use Python type hints throughout the codebase.

Example:

```python
def run_simulation(
    inputs: SimulationInput
) -> SimulationResult:
```

Prefer Pydantic models or dataclasses over loosely structured dictionaries.

---

## Code Quality

Write code that is easy to understand.

- Use descriptive variable names.
- Keep functions focused.
- Avoid giant 300-line functions.
- Remove duplicated logic.
- Extract reusable helper functions.
- Prefer explicit code over clever shortcuts.
- If a function exceeds roughly 50â€“75 lines, consider refactoring.

Future maintainers should understand the code without needing extensive explanations.

---

## Constants

Avoid magic numbers.

Instead of:

```python
iterations = 5000
```

Prefer:

```python
MC_ITERATIONS = 5000
```

Store shared constants in a dedicated constants or configuration module.

---

## Async Best Practices

Never block the event loop.

- Use `asyncio.gather()` whenever requests are independent.
- Wrap synchronous libraries with `asyncio.to_thread()`.
- Avoid serial execution when work can run concurrently.
- Always use reasonable timeout values.

---

## Prompt Management

Store prompts in dedicated files rather than embedding long prompt strings throughout the code.

Benefits include:

- easier prompt iteration
- cleaner Python code
- version control for prompts
- simpler debugging

---

## Caching

Cache expensive operations wherever possible.

Examples include:

- SEC responses
- FRED responses
- company metadata
- LLM outputs when appropriate

Always log cache hits and cache misses.

---

## Observability

Track important runtime metrics such as:

- API latency
- cache hit ratio
- cache miss ratio
- LLM latency
- Monte Carlo runtime
- total request latency

Performance bottlenecks should be easy to identify from logs.

---

## Documentation

Each major module should include a brief description covering:

- purpose
- inputs
- outputs
- responsibilities

Complex logic such as causal inference, Monte Carlo simulation, and DAG routing should include concise comments explaining *why* the implementation works, not just *what* it does.

---

## Git Practices

Maintain a clean Git history.

- Small atomic commits.
- Meaningful commit messages.
- Keep the `main` branch stable.
- Never commit secrets.
- Ignore `.env` files.
- Remove temporary debugging code before committing.

---

## Testing

Even during a hackathon, implement lightweight sanity tests for critical components:

- JSON schema validation
- DAG template routing
- Monte Carlo output shape
- cache behavior
- fallback mechanism
- API health endpoint

The objective is confidence, not exhaustive coverage.

---

## Performance Mindset

Optimize only after identifying bottlenecks.

Focus optimization efforts on:

- network I/O
- LLM inference
- Monte Carlo computation

Prefer readable code unless profiling demonstrates a measurable performance issue.

---

## Terminal Output

Keep terminal output clean and informative.

Avoid excessive logs that obscure useful information.

Color-coded or structured logs are encouraged during development to quickly distinguish:

- INFO
- WARNING
- ERROR
- SUCCESS

The terminal should provide a clear picture of the application's current state during execution.

---

## Dependency Management

Keep dependencies minimal.

Only install packages that are actively used.

Avoid adding large frameworks for problems that can be solved with lightweight libraries.

Regularly remove unused dependencies before submission.

---

## Naming Conventions

Maintain consistent naming throughout the project.

- Classes â†’ `PascalCase`
- Functions â†’ `snake_case`
- Variables â†’ `snake_case`
- Constants â†’ `UPPER_SNAKE_CASE`
- Files â†’ `snake_case.py`

Consistency improves readability across the entire codebase.

---

## Demo Stability First

When faced with the choice between:

- adding one more feature, or
- making the existing pipeline more reliable,

always prioritize reliability.

A polished, stable demonstration that succeeds every time is more valuable than additional features that introduce risk.

---

## Engineering Principle

Every piece of code added to the project should satisfy three questions:

1. **Is it readable?**
2. **Is it reliable?**
3. **Can another developer quickly understand and extend it?**

If the answer to any of these is **No**, refactor before moving on.
