import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def setup_logging(logging_config: dict) -> logging.Logger:
    """Configure application logging using the supplied settings."""
    level_name = logging_config.get("level", "INFO").upper()
    log_level = getattr(logging, level_name, None)

    if not isinstance(log_level, int):
        raise ValueError(f"Invalid logging level: {level_name}")

    log_format = logging_config.get(
        "format",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    log_file = Path(
        logging_config.get("file", "extraction.log")
    )

    if not log_file.is_absolute():
        log_file = PROJECT_ROOT / log_file

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding="utf-8")
    ]

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True
    )

    return logging.getLogger("sql_information_extraction")
