"""Middleware for request processing"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
        
        response.headers["X-Process-Time"] = str(process_time)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Handle errors globally"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Unhandled error: {str(e)}\n{tb}")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error": str(e),
                    "traceback": tb # Send traceback to frontend console for debugging
                }
            )
