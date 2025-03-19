import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings


class JsonLogger:
    """
    A logger wrapper that formats extra context as JSON strings in log messages.
    """

    def __init__(self, logger_name: str = "", level: int = logging.DEBUG):
        """
        Initialize with either a logger name or an existing logger object.

        Args:
            logger_name: Name to use when creating a new logger
        """
        self.logger = logging.getLogger(logger_name or __name__)
        self.logger.setLevel(level)

    def _log_with_json_extra(self, level: int, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """
        Log a message with the extra context formatted as JSON.

        Args:
            level: Logging level (e.g., logging.INFO)
            msg: Log message
            extra: Dictionary of extra context to include
            **kwargs: Additional keyword arguments for the logger
        """
        if extra:
            try:
                json_extra = json.dumps(extra)
                full_message = f"{msg} | extra={json_extra}"
                self.logger.log(level, full_message, exc_info=exc_info)
            except (TypeError, ValueError):
                self.logger.log(level, f"{msg} | extra={{unable to serialize}}", exc_info=exc_info)
        else:
            self.logger.log(level, msg, exc_info=exc_info)

    def setup_handler(self):
        """Add a console handler to the logger if none exists."""
        while self.logger.handlers:
            self.logger.removeHandler(self.logger.handlers[0])

        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] - [%(asctime)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return self

    def debug(self, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """Log a debug message with JSON-formatted extra context."""
        self._log_with_json_extra(logging.DEBUG, msg, extra, exc_info)

    def info(self, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """Log an info message with JSON-formatted extra context."""
        self._log_with_json_extra(logging.INFO, msg, extra, exc_info)

    def warning(self, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """Log a warning message with JSON-formatted extra context."""
        self._log_with_json_extra(logging.WARNING, msg, extra, exc_info)

    def error(self, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """Log an error message with JSON-formatted extra context."""
        self._log_with_json_extra(logging.ERROR, msg, extra, exc_info)

    def critical(self, msg: str, extra: dict[str, Any] | None = None, exc_info: bool = False):
        """Log a critical message with JSON-formatted extra context."""
        self._log_with_json_extra(logging.CRITICAL, msg, extra, exc_info)


# Configure logger
logger = JsonLogger("whatsapp-flows", logging.DEBUG if settings.DEBUG else logging.INFO)
logger.setup_handler()


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        request_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Add request_id to request state
        request.state.request_id = request_id

        # Log request
        logger.info(
            "Received request",
            extra={
                "request_id": request_id,
                "type": "request",
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Log response
        logger.info(
            "Sent response",
            extra={
                "request_id": request_id,
                "type": "response",
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        return response
