import sys
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s >>> %(filename)s:%(lineno)d >>> %(message)s')

log_file_handler = RotatingFileHandler("logs/main.log", maxBytes=1024 * 1024 * 1, backupCount=3)
log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
