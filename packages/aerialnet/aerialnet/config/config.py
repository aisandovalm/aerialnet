import pathlib
import os
from PIL import Image, ImageDraw, ImageFont
import aerialnet
 
#PWD = os.path.dirname(os.path.abspath(__file__))
#PACKAGE_ROOT = os.path.abspath(os.path.join(PWD, '..'))
PACKAGE_ROOT = pathlib.Path(aerialnet.__file__).resolve().parent
DATA_DIR = os.path.join(PACKAGE_ROOT, 'data')
SAVED_MODEL_DIR = os.path.join(PACKAGE_ROOT, 'saved_models')

# Tensorflow Serving
GRPC_SERVER = '127.0.0.1:8500'

# Image utils
fontpath = os.path.join(DATA_DIR, 'Ubuntu-Th.ttf')
FONTSIZE=10
FONT = ImageFont.truetype(fontpath, FONTSIZE)

# Labels map
labels = open(os.path.join(DATA_DIR, 'classes.csv')).read().strip().split('\n')
LABELS = {int(L.split(",")[1]): L.split(",")[0] for L in labels}
 
with open(os.path.join(PACKAGE_ROOT, 'VERSION')) as version_file:
    _version = version_file.read().strip()

fileLogger = None