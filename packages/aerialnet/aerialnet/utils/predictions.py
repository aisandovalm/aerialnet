import tensorflow as tf
import numpy as np
from aerialnet.utils.nms import non_max_suppression_all_classes
from aerialnet.utils.colors import label_color
from aerialnet.utils.classes import label_classname

from PIL import Image, ImageDraw, ImageFont
import cv2
import logging

_logger = logging.getLogger(__name__)

def extract_predictions(result_future, threshold=0.35):
    """Callback function.
    Calculates the statistics for the prediction result.
    Args:
    result_future: Result future of the RPC.
    """
    boxes = result_future.\
        outputs['filtered_detections/map/TensorArrayV2Stack/TensorListStack:0']
    scores = result_future.\
        outputs['filtered_detections/map/TensorArrayV2Stack_1/TensorListStack:0']
    labels = result_future.\
        outputs['filtered_detections/map/TensorArrayV2Stack_2/TensorListStack:0']

    boxes= tf.make_ndarray(boxes)
    scores= tf.make_ndarray(scores)
    labels= tf.make_ndarray(labels)

    # Filter weak detections
    threshold_mask = np.greater_equal(scores[0], threshold)
    threshold_boxes = boxes[0][threshold_mask]
    threshold_scores = scores[0][threshold_mask]
    threshold_labels = labels[0][threshold_mask]

    # sort values by score
    sorted_mask = np.argsort(threshold_scores)[::-1]
    sorted_boxes = threshold_boxes[sorted_mask]
    sorted_scores = threshold_scores[sorted_mask]
    sorted_labels = threshold_labels[sorted_mask]

    # perform non-max-supression
    included_indices = np.asarray(non_max_suppression_all_classes(sorted_boxes, sorted_scores, sorted_labels, 0.5))
    selected_boxes = sorted_boxes[included_indices]
    selected_scores = sorted_scores[included_indices]
    selected_labels = sorted_labels[included_indices]

    return selected_boxes, selected_scores, selected_labels

def parse_predictions(nn_output, font, fontsize, labels, imgArr=None, threshold=0.35, thickness=1):
    response_data = {"success": True}
    response_data["predictions"] = []

    try:
        selected_boxes, selected_scores, selected_labels = extract_predictions(nn_output, threshold)
    except IndexError:
        _logger.exception('Empty array while extracting predictions')
        response_data = {"predictions": [], "success": False, "message": "Sin detecciones"}
        return response_data, None
    except Exception:
        _logger.exception('Exception while extracting predictions')
        response_data = {"predictions": [], "success": False, "message": "Sin detecciones"}
        return response_data, None

    if imgArr is not None:
        img_pil = Image.fromarray(imgArr)
        draw = ImageDraw.Draw(img_pil)

    # loop over detections
    for (bbox, score, label) in zip(selected_boxes, selected_scores, selected_labels):
        # convert bounding box coordinates from float to int
        bbox = bbox.astype(int)
        predicted_class = label_classname(int(labels[label]))
        score = int(score*100)
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])

        # append prediction
        c_prediction = {"label": predicted_class, "score": score, "x1": x1, "y1": y1, 
        "x2": x2, "y2": y2, "xc": int(x1 + (x2-x1)/2), "yc": int(y1 + (y2-y1)/2)}
        response_data["predictions"].append(c_prediction)
        
        if imgArr is not None:
            text = predicted_class + ' {}%'.format(score)
            #Determina el color de la marca en base a la clase
            color = label_color(label)
            draw.rectangle([(x1,y1),(x2,y2)], outline=color, width=thickness)
            draw.rectangle([(x1,y1-7),(x2,y1)], outline=color, width=6)
            draw.text((x1,y1-fontsize/2-4), text, font = font, fill=(255,255,255))
            
    if imgArr is not None:
        outputImg = np.array(img_pil)
    else:
        outputImg = None

    return response_data, outputImg
