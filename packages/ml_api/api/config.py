import logging
from logging.handlers import TimedRotatingFileHandler
import pathlib
import os
import sys
 
PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent
 
FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s —"
    "%(funcName)s:%(lineno)d — %(message)s")
LOG_DIR = pathlib.Path(os.path.join(PACKAGE_ROOT, 'logs'))
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = pathlib.Path(os.path.join(LOG_DIR, 'ml_api.log'))
OUTPUT_FOLDER = pathlib.Path(os.path.join(PACKAGE_ROOT, 'outputs'))
OUTPUT_FOLDER.mkdir(exist_ok=True)
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler
 
 
def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when='midnight', interval=1)
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.INFO)
    return file_handler
 
 
def get_logger(*, logger_name):
    """Get logger with prepared handlers."""
 
    logger = logging.getLogger(logger_name)
 
    logger.setLevel(logging.INFO)
 
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
 
    return logger

 
class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'pum-2020'
    SERVER_PORT = 5000
    OUTPUT_FOLDER = OUTPUT_FOLDER
 
 
class ProductionConfig(Config):
    DEBUG = False
    SERVER_ADDRESS: os.environ.get('SERVER_ADDRESS', '0.0.0.0')
    SERVER_PORT: os.environ.get('SERVER_PORT', '5000')
 
 
class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    USE_RELOADER = True
 
 
class TestingConfig(Config):
    TESTING = True