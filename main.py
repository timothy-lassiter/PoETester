import logging
from logging.handlers import RotatingFileHandler

from app import run, APP_NAME

handler = RotatingFileHandler(f"{APP_NAME}.log", maxBytes=100_000_000, backupCount=2)
logging.basicConfig(level=logging.WARN, handlers=[handler])

run()
