"""
Logging configuration using Loguru.
"""
import sys
import json
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import settings

# Remove default logger
logger.remove()


def serialize(record: dict[str, Any]) -> str:
    """Serialize log record to JSON."""
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
    }

    if record.get("extra"):
        subset["extra"] = record["extra"]

    if record.get("exception"):
        subset["exception"] = record["exception"]

    return json.dumps(subset)


def formatter(record: dict[str, Any]) -> str:
    """Format log record."""
    if settings.LOG_FORMAT == "json":
        return serialize(record) + "\n"

    # Default colored format for development
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>\n"
    )


# Configure logger
def configure_logging() -> None:
    """Configure application logging."""

    # Console handler
    logger.add(
        sys.stdout,
        format=formatter,
        level=settings.LOG_LEVEL,
        colorize=settings.LOG_FORMAT != "json",
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )

    # File handler for errors
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logger.add(
        log_path / "error.log",
        format=formatter,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # File handler for all logs
    logger.add(
        log_path / "app.log",
        format=formatter,
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )

    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}")


# Export logger instance
__all__ = ["logger", "configure_logging"]
