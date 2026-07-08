import time
import jwt

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from log import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        user = "anonymous"
        error_occured = False

        token = request.cookies.get("access_token")

        if token:
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user = payload.get("sub", "unknown")
            except Exception:
                user = "invalid_token"
        try:
            response = await call_next(request)
            if response.status_code >= 500:
                error_occured = True
                logger.error(
                    f"Server error: {request.method} {request.url.path} - User: {user} - Status code: {response.status_code}"
                )
            return response

        except Exception as e:
            error_occured = True
            logger.error(
                f"Exception occured during request: {request.method} {request.url.path} - User: {user} - Error: {str(e)}"
            )
            raise
        finally:
            if not error_occured:
                process_time = time.time() - start_time
                logger.info(
                    f"SUCCESS: {request.method} {request.url.path} | User: {user} | Time: {process_time:.4f}s"
                )
