import os
from aerialnet.config import config

 
VERSION_PATH = os.path.join(config.PACKAGE_ROOT, 'VERSION')
 
# Configure logger for use in package
'''print('aerialnet logger: {}'.format(__name__))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging_config.get_console_handler())
logger.propagate = True'''
 
with open(VERSION_PATH, 'r') as version_file:
    __version__ = version_file.read().strip()