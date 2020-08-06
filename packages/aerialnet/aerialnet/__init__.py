import logging
import os
from aerialnet.config import config
from aerialnet.config import logging_config
 
 
VERSION_PATH = os.path.join(config.PACKAGE_ROOT, 'VERSION')
 
# Configure logger for use in package
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging_config.get_console_handler())
logger.propagate = False
 
 
with open(VERSION_PATH, 'r') as version_file:
    __version__ = version_file.read().strip()
 

