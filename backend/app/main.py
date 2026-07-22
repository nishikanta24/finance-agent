import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.features.ingestion.router import router as ingestion_router
from app.features.analysis.router import router as analytics_router

# Configure logging standard
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Agentic Decision Intelligence Engine",
    description="AMD Hackathon Track 3 Backend Service",
    version="1.0.0",
)

# Enable CORS for local development ports
origins = [
    "http://localhost",
    "http://localhost:3000", # Common React dev port
    "http://localhost:5173", # Common Vite dev port
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Agentic Decision Intelligence Engine...")
    logger.info(f"Using latency budget: {settings.LATENCY_BUDGET}")
    if not settings.FIREWORKS_API_KEY:
        logger.warning(
            "FIREWORKS_API_KEY is not defined in the environment. "
            "Please create a .env file based on .env.example."
        )

@app.get("/health")
async def health_check():
    """
    FastAPI health check endpoint.
    Strictly async function to adhere to the I/O-bound guidelines.
    """
    logger.info("Health check endpoint hit.")
    return {
        "status": "engine_running",
        "latency_budget": settings.LATENCY_BUDGET
    }
