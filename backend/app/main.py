"""
IP-SAKTI Sahayak Backend
Bridges the React frontend, the Python RAG engine / LLM inference service,
and PostgreSQL.
"""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.config import settings
from app.database import Base, engine
from app.documents.router import router as documents_router
from app.feedback.router import router as feedback_router
from app.novelty.router import router as novelty_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ipsakti")

# Create tables if they don't exist yet (use Alembic migrations in production).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for IP-SAKTI Sahayak — a multilingual AI assistant for "
        "Intellectual Property and Ayurveda regulatory guidance. This service "
        "bridges the React frontend, the Python RAG retrieval pipeline, the "
        "LLM inference service, and PostgreSQL."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handling
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Validation failed."},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(novelty_router)

@app.get("/", tags=["Health"])
def root() -> dict:
    return {"service": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "healthy"}
