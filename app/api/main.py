"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.utils.logger import get_logger
from app.api.routes import logs, rules, actions

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GiftPulse - Twilio Log Monitor",
    description="Monitor Twilio logs and trigger automated actions",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "giftpulse-monitor", "version": "0.1.0"}


# Include routers
app.include_router(logs.router, prefix="/api", tags=["Logs"])
app.include_router(rules.router, prefix="/api", tags=["Rules"])
app.include_router(actions.router, prefix="/api", tags=["Actions"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting GiftPulse Twilio Log Monitor API")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down GiftPulse Twilio Log Monitor API")
