from typing import Any, Dict, Optional
import json
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.models import AsyncSessionLocal, AuditLog
from src.utils.sanitization import sanitize_data

logger = structlog.get_logger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.state_changing_methods = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        # We only audit state-changing methods
        if request.method not in self.state_changing_methods:
            return await call_next(request)

        # To read the body multiple times, we need to cache it
        # Note: This can be memory intensive for very large bodies
        body_bytes = await request.body()
        
        # Replace request body to let follow-up middleware or route read it
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        
        # We create a new request object with the cached body
        # Alternatively, we can just use the body_bytes directly for logging
        
        # Process request
        response = await call_next(request)
        
        # After response, log to AuditLog
        try:
            # Attempt to parse body as JSON for logging
            inputs = None
            if body_bytes:
                try:
                    inputs = json.loads(body_bytes.decode())
                except:
                    inputs = {"raw_body": body_bytes.decode(errors="ignore")}

            # Sanitize inputs
            sanitized_inputs = sanitize_data(inputs)
            
            # Get Correlation ID from request state or headers
            correlation_id = request.headers.get("X-Correlation-ID")
            
            # Get Agent ID if present (might be in headers or path)
            agent_id = request.headers.get("X-Agent-ID")
            
            # Log to Database
            async with AsyncSessionLocal() as session:
                audit_entry = AuditLog(
                    action=f"{request.method} {request.url.path}",
                    agent_id=agent_id,
                    inputs=sanitized_inputs,
                    outputs={"status_code": response.status_code},
                    correlation_id=correlation_id,
                )
                session.add(audit_entry)
                await session.commit()
                
        except Exception as e:
            # We don't want audit logging failures to crash the main request
            logger.error("audit_logging_failed", error=str(e), path=request.url.path)

        return response
