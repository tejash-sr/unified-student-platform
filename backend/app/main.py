"""
Main FastAPI application entry point.
Initializes routes, middleware, and core services.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.core import init_db, health_check, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifecycle manager.
    Runs startup and shutdown logic.
    """
    # Startup
    logger.info("🚀 Starting Unified Student Platform API...")
    try:
        init_db()
        logger.info("✅ Database initialized")
        
        # Initialize vector DB and embeddings (lazy loaded, will initialize on first use)
        from app.utils import get_vector_db, get_embedding_service
        logger.info("📊 Embedding service ready (lazy loaded)")
        logger.info("🔍 Vector DB ready (ChromaDB)")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down gracefully...")


# Initialize FastAPI app
app = FastAPI(
    title="Unified Student Platform API",
    description="AI-first engagement platform for students planning higher education",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint."""
    db_status = "healthy" if health_check() else "unhealthy"
    
    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.environment,
        "service": "Unified Student Platform API",
    }


@app.get("/info", tags=["System"])
async def info():
    """API information endpoint."""
    return {
        "name": "Unified Student Platform API",
        "version": "1.0.0",
        "environment": settings.environment,
        "features": [
            "User Management",
            "University & Course Discovery",
            "Application Tracking",
            "Loan Eligibility & Calculator",
            "AI-Driven Recommendations",
            "ROI Analysis",
            "Application Timeline Generator",
            "Analytics & Engagement Tracking",
        ],
    }


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# Import routes
from app.routes import users, loans, growth
from app.routes.courses_universities import courses_router, universities_router, recommendations_router

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(loans.router, prefix="/api/loans", tags=["Loans"])
app.include_router(growth.router, prefix="/api/growth", tags=["Growth Engine"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(universities_router, prefix="/api/universities", tags=["Universities"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API documentation links."""
    return {
        "message": "Welcome to Unified Student Platform API",
        "documentation": "/api/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
