"""
Logging-Modul für SpriteForge.
Stellt eine zentrale Logging-Konfiguration bereit.
"""

import logging
import logging.handlers
import os
from pathlib import Path
import json
import datetime


class CustomJSONFormatter(logging.Formatter):
    """JSON-Formatter für strukturierte Logs."""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "component"):
            log_record["component"] = record.component

        return json.dumps(log_record, ensure_ascii=False)


def get_logger(name="spriteforge"):
    """
    Gibt einen konfigurierten Logger zurück.

    Args:
        name: Name des Loggers

    Returns:
        logging.Logger: Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    return logger


def setup_logger():
    """Konfiguriert das Logging-System."""
    formatter = CustomJSONFormatter()
    log_level = os.getenv("LOG_LEVEL", "ERROR").upper()

    # Log-Verzeichnis
    log_dir = Path.cwd() / "logs" / datetime.datetime.now().strftime("%d-%m-%Y")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Root-Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Existierende Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Konsolenausgabe
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Datei-Logger
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "spriteforge.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Externe Bibliotheken
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)

    # Flet Framework auf WARNING - verhindert massive DEBUG-Ausgaben
    logging.getLogger("flet").setLevel(logging.WARNING)
    logging.getLogger("flet_core").setLevel(logging.WARNING)
    logging.getLogger("flet_runtime").setLevel(logging.WARNING)

    root_logger.info(f"Logger initialisiert. Log-Verzeichnis: {log_dir}")

    return root_logger
