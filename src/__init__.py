import os

from loguru import logger

log_dir = os.environ.get('LOG_DIR', './logs/')
logger.add(os.path.join(log_dir, 'file_{time}.log'))