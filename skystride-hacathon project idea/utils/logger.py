import logging
import os

# Ensure the logs/ directory exists relative to the project root
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, "app.log")

# Build logger
logger = logging.getLogger("skystride")
logger.setLevel(logging.INFO)

# Avoid duplicate handlers if the module is reloaded
if not logger.handlers:
    _fmt = logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s")

    # Console handler
    _stream_handler = logging.StreamHandler()
    _stream_handler.setLevel(logging.INFO)
    _stream_handler.setFormatter(_fmt)
    logger.addHandler(_stream_handler)

    # File handler
    _file_handler = logging.FileHandler(log_file, encoding="utf-8")
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(_fmt)
    logger.addHandler(_file_handler)
