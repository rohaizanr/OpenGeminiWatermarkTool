"""Structured logging configuration"""

import json
import logging
import sys
from datetime import datetime
from typing import Any

from .config import get_settings


class JSONFormatter(logging.Formatter):
    """Format logs as JSON with structured fields"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            # Anonymize IP: keep first 3 octets for IPv4, first 4 groups for IPv6
            ip = record.ip_address
            if ":" in ip:  # IPv6
                parts = ip.split(":")
                log_data["ip_address"] = ":".join(parts[:4]) + ":xxxx:xxxx:xxxx:xxxx"
            else:  # IPv4
                parts = ip.split(".")
                log_data["ip_address"] = ".".join(parts[:3]) + ".xxx"
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure application logging"""
    settings = get_settings()

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on environment
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module"""
    return logging.getLogger(name)
