import logging
from typing import Optional


def configure_logging(level_name: Optional[str] = None) -> None:
    level = getattr(logging, (level_name or "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(name)s - %(message)s')


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


