import os
import logging
import logging.config
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, cast 
from src.zyro.core.setting import ensure_directories, get_settings


def setup_logging() -> RotatingFileHandler:
    """Application logging configuration."""

    settings = get_settings()
    ensure_directories()

    # Create a log file with timestamp
    log_filename = os.path.join(
        settings.logs_directory,
        f"zyro_{datetime.now().strftime('%Y%m%d')}.log"
    )

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
                )
            },
            "console": {
                "format": "%(levelname)s:\t%(message)s"
            },
            "json": {
                "format": (
                    '{"timestamp": "%(asctime)s", "logger": "%(name)s", '
                    '"level": "%(levelname)s", "file": "%(filename)s", '
                    '"line": %(lineno)d, "function": "%(funcName)s", '
                    '"message": "%(message)s"}'
                )
            }
        },

        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": log_filename,
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
                "stream": "ext://sys.stdout"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": os.path.join(settings.logs_directory, "errors.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5
            }
        },

        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["file", "error_file", "console"], 
                "propagate": False
            },
        },

        "root": {
            "level": "INFO",
            "handlers": ["file", "console", "error_file"]
        }
    }

    logging.config.dictConfig(logging_config)

    return cast(RotatingFileHandler, logging.getLogger().handlers[0])

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""

    return logging.getLogger(f"zyro.{name}")

class Logger:
    """Class to provide logging functionality."""

    @property
    def logger(self) -> logging.Logger:
        """logger for the class."""

        return get_logger(self.__class__.__name__) 