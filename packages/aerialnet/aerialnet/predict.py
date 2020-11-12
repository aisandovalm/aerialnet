import numpy as np
import os
import io
from aerialnet.config import config
from aerialnet import __version__ as _version
from aerialnet.utils.predictions import parse_predictions
from aerialnet.utils.image import read_image_bgr, preprocess_image
 
import logging
import typing as t
from timeit import default_timer as timer

import grpc
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

import cv2
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

grpcChannel = grpc.insecure_channel(config.GRPC_SERVER)
grpcStub = prediction_service_pb2_grpc.PredictionServiceStub(grpcChannel)
 
#_logger = logging.getLogger(__name__)

THRESHOLD = 0.68
def make_prediction(imgBytesContent, imgURL, generateOutputImg=False, outputPath=None):
    """Make a prediction using a saved model pipeline.
 
    Args:
        input_data: Array of model prediction inputs.
 
    Returns:
        Predictions for each input row, as well as the model version.
    """
 
    start = timer()

    pilImg = Image.open(io.BytesIO(imgBytesContent))
    img_path = os.path.join(config.DATA_DIR, 'pil_tmp_img.jpg')
    pilImg.save(img_path)

    image = read_image_bgr(img_path)
    cvImg = cv2.imread(img_path)
    image = preprocess_image(image)
    inputImg = np.expand_dims(image, axis=0)

    # Send request
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'aerialnet'
    request.model_spec.signature_name = 'serving_default'
    
    request.inputs['input_image'].CopyFrom(
        tf.make_tensor_proto(inputImg, shape=inputImg.shape))
    result = grpcStub.Predict(request, 60.0)  # 60 secs timeout

    processing_time = round(timer() - start, 2)
    
    start = timer()
    if generateOutputImg:
        response_data, outputImg = parse_predictions(result, imgURL, config.FONT, config.FONTSIZE, config.LABELS, cvImg, threshold=THRESHOLD)
        if outputImg is not None:
            cv2.imwrite(outputPath, outputImg)
    else:
        response_data, _ = parse_predictions(result, imgURL, config.FONT, config.FONTSIZE, config.LABELS, threshold=THRESHOLD)
    parsing_time = round(timer() - start, 2)
 
    config.fileLogger.info(
        f"Predicting image {imgURL} with model version: {_version} "
        f"Processing time: {processing_time} seconds "
        f"Parsing time: {parsing_time} seconds "
        f"Predictions: {response_data} "
    )
 
    return response_data
 
 

