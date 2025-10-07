import json
import logging
import sys
from typing import Any, Dict

_logger = logging.getLogger("merlin")
_logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(message)s"))
if not _logger.handlers:
    _logger.addHandler(_handler)


def log_event(event: str, **fields: Any) -> None:
    record: Dict[str, Any] = {"event": event, **fields}
    try:
        _logger.info(json.dumps(record, ensure_ascii=False))
    except Exception:
        _logger.info(json.dumps({"event": "log_error", "original_event": event}))
