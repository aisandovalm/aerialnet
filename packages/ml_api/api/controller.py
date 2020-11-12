from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

import os
import io
import numpy as np

import json

import requests
from timeit import default_timer as timer

import traceback

from api.config import get_logger, OUTPUT_FOLDER
from api import __version__ as api_version
from aerialnet.predict import make_prediction
import aerialnet.config as aerialnet_config

_logger = get_logger(logger_name=__name__)
aerialnet_config.fileLogger = _logger
 
prediction_app = Blueprint('prediction_app', __name__)
 
@prediction_app.route('/health', methods=['GET'])
def health():
    if request.method == 'GET':
        _logger.info('health status OK')
        return 'ok'
 
 
@prediction_app.route('/version', methods=['GET'])
def version():
    if request.method == 'GET':
        return jsonify({'model_version': 5,
                        'api_version': api_version})
 
@prediction_app.route('/predict', methods=['POST'])
def predict():
    _logger.info(f'New prediction request')
    # initialize the data dictionary that will be returned from the
    # view
    output = ""

    # ensure an image was properly uploaded to our endpoint
    if request.method == "POST":
        try:
            try:
                img_url = request.form["img_url"]
            except:
                img_url = ""

            try:
                generateOutputImg = bool(int(request.form["output_img"]))
            except:
                generateOutputImg = bool(0)

            if img_url != "":
                _logger.info(f'Getting image {img_url} from blob storage')
                image_bytes = requests.get(img_url)
                
                if image_bytes != "BlobNotFound":
                    if generateOutputImg:
                        outputImgPath = os.path.join(OUTPUT_FOLDER, img_url.split('/')[-1])
                        if '.jpg' in outputImgPath or '.JPG' in outputImgPath:
                            pass
                        else:
                            _logger.warning(f'Incorrect path for output image {outputImgPath}')
                            generateOutputImg = False
                            outputImgPath = None
                    else:
                        outputImgPath = None

                    response_data = make_prediction(image_bytes.content, imgURL=img_url, generateOutputImg=generateOutputImg, outputPath=outputImgPath)

                    output =  jsonify(response_data)
                else:
                    output = jsonify({"predictions": [], "success": False, "message": image_bytes})
        except Exception as e:
            tb = traceback.format_exc()
            _logger.exception(f'Exception on Flask server (predict function): {e} \n \
                traceback: {tb}')
        finally:
            return output