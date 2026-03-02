import logging
import sys
import time
import uuid
from typing import Any, Dict

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Agentic Trading Platform API",
    version=settings.version,
    description="Backend API for managing trading agents and risk",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for correlation ID and request logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(
        "request_processed",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=process_time,
    )
    return response

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = structlog.contextvars.get_contextvars().get("correlation_id", "unknown")
    
    error_type = type(exc).__name__
    error_detail = str(exc)
    
    logger.error(
        "unhandled_exception",
        error=error_type,
        detail=error_detail,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": error_detail if settings.app_env == "development" else "An unexpected error occurred",
            "correlation_id": correlation_id,
        },
    )

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.version,
        "environment": settings.app_env,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
