import sys
import logging
from logging.handlers import RotatingFileHandler

formatter = logging.Formatter('%(asctime)s:%(levelname)s >>> %(filename)s:%(lineno)d >>> %(message)s')

log_file_handler = RotatingFileHandler(
    "Proxy_Server/file_celery/logs/celery.log",
    maxBytes=1024 * 1024 * 1,
    backupCount=3
)

log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)
