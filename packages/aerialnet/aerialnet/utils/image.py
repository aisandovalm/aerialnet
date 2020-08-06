from aerialnet.utils.colors import label_color
from aerialnet.utils.classes import label_classname
import aerialnet.config as config

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import io

#from azure.storage.blob import BlockBlobService, PublicAccess

def read_image_bgr(path):
    """ Read an image in BGR format.

    Args
        path: Path to the image.
    """
    # We deliberately don't use cv2.imread here, since it gives no feedback on errors while reading the image.
    image = np.ascontiguousarray(Image.open(path).convert('RGB'))
    return image[:, :, ::-1]


def preprocess_image(x, mode='caffe'):
    """ Preprocess an image by subtracting the ImageNet mean.

    Args
        x: np.array of shape (None, None, 3) or (3, None, None).
        mode: One of "caffe" or "tf".
            - caffe: will zero-center each color channel with
                respect to the ImageNet dataset, without scaling.
            - tf: will scale pixels between -1 and 1, sample-wise.

    Returns
        The input with the ImageNet mean subtracted.
    """
    # mostly identical to "https://github.com/keras-team/keras-applications/blob/master/keras_applications/imagenet_utils.py"
    # except for converting RGB -> BGR since we assume BGR already

    # covert always to float32 to keep compatibility with opencv
    x = x.astype(np.float32)

    if mode == 'tf':
        x /= 127.5
        x -= 1.
    elif mode == 'caffe':
        x -= [103.939, 116.779, 123.68]

    return x

def render(img:np.ndarray, boxes, scores, labels, LABELS, thickness=1) -> np.ndarray:
    """ Dibuja las marcas en una imagen """

    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)

    # loop over detections
    for (bbox, score, label) in zip(boxes, scores, labels):
        # convert bounding box coordinates from float to int
        bbox = bbox.astype(int)
        text = label_classname(int(LABELS[label])) + ' {}%'.format(int(score*100))
        #Determina el color de la marca en base a la clase
        color = label_color(label)

        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[2]
        y2 = bbox[3]
        
        draw.rectangle([(x1,y1),(x2,y2)], outline=color, width=thickness)
        
        draw.rectangle([(x1,y1-7),(x2,y1)], outline=color, width=6)
        draw.text((x1,y1-config.FONTSIZE/2-4), text, font = config.FONT, fill=(255,255,255))
            
    img = np.array(img_pil)
    return img