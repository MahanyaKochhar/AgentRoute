"""Shared INFO logging configuration for application diagnostics."""
import logging
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "app.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        from src.metrics import current_metrics
        metrics = current_metrics.get()
        record.request_id = metrics.request_id if metrics else "-"
        record.approach = metrics.approach if metrics else "-"
        return True


logger = logging.getLogger("src")
logger.setLevel(logging.INFO)
# Keep application events out of the server/root console handlers.
logger.propagate = False
if not any(isinstance(handler, logging.FileHandler) and
           handler.baseFilename == str(LOG_FILE) for handler in logger.handlers):
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.addFilter(RequestContextFilter())
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s request_id=%(request_id)s approach=%(approach)s %(name)s %(message)s"))
    logger.addHandler(handler)
