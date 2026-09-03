import os
import logging
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists relative to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(project_root, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "trading_bot.log")

# Configure logger
logger = logging.getLogger("trading_bot")
logger.setLevel(logging.INFO)

# Prevent log propagation to root logger if root has other handlers
logger.propagate = False

# Clear any existing handlers to avoid duplicates on reload
if logger.hasHandlers():
    logger.handlers.clear()

# Formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] (%(name)s) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File Handler
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# Console Handler
console_handler = logging.StreamHandler()
def redact_sensitive(data):
    """Recursively search and redact sensitive fields in dictionaries or strings."""
    if isinstance(data, dict):
        redacted = {}
        sensitive_keys = {"signature", "api_key", "secret_key", "BINANCE_API_KEY", "BINANCE_SECRET_KEY"}
        for k, v in data.items():
            if k in sensitive_keys or any(s in k.upper() for s in ["KEY", "SECRET", "SIGNATURE"]):
                redacted[k] = "********"
            else:
                redacted[k] = redact_sensitive(v)
        return redacted
    elif isinstance(data, list):
        return [redact_sensitive(item) for item in data]
    elif isinstance(data, str):
        # Redact signatures and keys in query string formats
        import re
        # Redact signature=...
        data = re.sub(r"signature=[a-zA-Z0-9]+", "signature=********", data)
        # Redact X-MBX-APIKEY value in query/log
        data = re.sub(r"X-MBX-APIKEY:[a-zA-Z0-9_-]+", "X-MBX-APIKEY:********", data)
    return data
