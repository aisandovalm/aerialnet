# import packages
import os, sys
import glob
import pandas as pd
import argparse
import random
import csv
import cv2
import math
import json
import requests
from PIL import Image
import io
#from utils.classes import label_classname, label_classnumber

def convert(list): 
    return (*list, ) 

def intersection_ratio(boxPatch, boxObj):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxPatch[0], boxObj[0])
    yA = max(boxPatch[1], boxObj[1])
    xB = min(boxPatch[2], boxObj[2])
    yB = min(boxPatch[3], boxObj[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    if interArea <= 0:
        return 0
    else:
        # compute the area of both the prediction and ground-truth
        # rectangles
        #boxPatchArea = (boxPatch[2] - boxPatch[0] + 1) * (boxPatch[3] - boxPatch[1] + 1)
        boxObjArea = (boxObj[2] - boxObj[0] + 1) * (boxObj[3] - boxObj[1] + 1)
        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        #iou = interArea / float(boxPatchArea + boxObjArea - interArea)
        ir = interArea / boxObjArea
        # return the intersection over union value
        return ir

def check_obj_in_patch(bboxObj, bboxPatch):
    objX1, objY1, objX2, objY2 = bboxObj
    patchX1, patchY1, patchX2, patchY2 = bboxPatch
    if patchX1 < objX1 < patchX2 and patchX1 < objX2 < patchX2:
        pass
    else:
        # add objects with enough area inside the patch
        if intersection_ratio(bboxPatch, bboxObj) > 0.5:
            pass
        else:
            return False

    if patchY1 < objY1 < patchY2 and patchY1 < objY2 < patchY2:
        pass
    else:
        # add objects with enough area inside the patch
        if intersection_ratio(bboxPatch, bboxObj) > 0.7:
            pass
        else:
            return False
    return True

def get_img(imgURL, outputDir):
    try:
        imgName = imgURL.split('/')[-1]
        imgPath = os.path.join(outputDir, imgName)

        # check if image was already processed
        if len(glob.glob(imgPath.replace('.jpg', '').replace('.JPG', '')+'*')) > 0:
            print('Image {} was already processed'.format(imgName))
            return None, None, None

        print('Downloading image: {}'.format(imgURL))
        image_bytes = requests.get(imgURL)
        pilImg = Image.open(io.BytesIO(image_bytes.content))

        # save original image
        pilImg.save(imgPath)
        cvImg = cv2.imread(imgPath)
    except OSError:
        return None, None, None

    return cvImg, imgPath, imgName

def check_one_class_only(regions, _class):
    for region in regions: # loop over every annotation in the image
        # if is the class, then go to the next one
        if region['region_attributes']['clase'] == _class:
            pass
        else:
            # if it is a different class, then return False (there are other classes in the image)
            return False

    return True

def get_class_idx(dict, classId=None, className=None):
    if className is not None:
        return next((i for i, item in enumerate(dict) if item['name'] == className), None)
    if classId is not None:
        return next((i for i, item in enumerate(dict) if item['id'] == classId), None)
    return None

# Construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("--mode", help="Mode: 'train' to generate train and val datasets, 'test' to generate test dataset")
ap.add_argument("--datasetSourceDir", help = "Path to dataset source directory")
ap.add_argument("--datasetVersionDir", help = "Path to the directory to write the output imgs")
ap.add_argument("--classesFilePath", help = "Path to classes file")
ap.add_argument("--trainOutputCSV", help = "Path to the train file to write the output")
ap.add_argument("--valOutputCSV", help = "Path to the validation file to write the output")
ap.add_argument("--testOutputCSV", help = "Path to the test file to write the output")
ap.add_argument("--patchSize", default = 1000, type = int, help = "size of square image in px")
ap.add_argument("--split", default = 0.95, type = float, help = "train/val split")
ap.add_argument("--keepEmpty", default = False, action='store_true', help = "If we keep patch images with 0 labels")

args = vars(ap.parse_args())

# build paths and create var names for all arguments
# inputs
if args['mode'] == 'train':
    STRIDE = args["patchSize"]-200
    OUTPUT_IMGS_PATH = os.path.join(args["datasetVersionDir"], 'imgs')
    os.makedirs(OUTPUT_IMGS_PATH, exist_ok=True)
if args['mode'] == 'test':
    INPUT_TEST_FILE = args['inputFilePath']

    OUTPUT_CSV_TEST = args['testFilePath']

# Read classes
classesDict = []
with open(args['classesFilePath'], 'r') as f:
    lines = f.readlines()
    for line in lines:
        classNum, className = line.split(',')
        classesDict.append({'id': classNum, 'name': className.replace('\n', ''), 'count': 0})

print("[INFO] creating dataset with {} classes: {}".format(len(classesDict), classesDict))

if args["mode"] == 'train':
    # Generate list of files
    fileList = []
    for (dirpath, _, filenames) in os.walk(args['datasetSourceDir']):
        jsonFiles = [os.path.abspath(os.path.join(dirpath, fileName)) \
            for fileName in filenames if (fileName.endswith('.json') and "SOURCE" in fileName)]
        fileList.extend(jsonFiles)
    print('[INFO] Found {} annotation files (JSON): {}'.format(len(fileList), fileList))
    
    #sys.exit()
    random.seed(0.1)

    # annotation objects
    annTrain = []
    annTest = []
    # annotations counter
    no_trainExamples = 0
    no_valExamples = 0
    # images counter
    no_trainImg = 0
    no_valImg = 0

    # open the output CSV files
    with open(args['trainOutputCSV'], "w") as trainCSV, open(args['valOutputCSV'], "w") as valCSV:
        trainWriter = csv.writer(trainCSV)
        valWriter = csv.writer(valCSV)

        # loop over annotation files
        for ANNOTATION_PATH in fileList:
            # read next annotation file
            with open(ANNOTATION_PATH, 'r') as dataset:
                # load content
                jsonDataset = json.load(dataset)

                # loop over images
                for imgAnnIdx in jsonDataset:
                    imgAnn = jsonDataset[imgAnnIdx]
                    dType = random.choices(['train', 'val'], weights=(args["split"], 1-args["split"]), k=1)[0]
                    # generate corresponding annotation path

                    # get data
                    print('[INFO] Analizing image: {}'.format(imgAnn['filename']))
                    cvImg, imgLocalPath, imgName = get_img(imgAnn['filename'], OUTPUT_IMGS_PATH)
                    
                    if cvImg is None:
                        continue

                    # image boundaries
                    imgHeight, imgWidth, _ = cvImg.shape

                    #############################################
                    no_xPatches = math.ceil(imgWidth / args["patchSize"])
                    no_yPatches = math.ceil(imgHeight / args["patchSize"])
                    no_Patches = 0

                    for xP in range(no_xPatches):
                        for yP in range(no_yPatches):
                            # EACH PATCH
                            # get patch boundaries
                            if xP == no_xPatches - 1:
                                xPMax = imgWidth
                                xPMin = xPMax - args["patchSize"]
                            else:
                                xPMin = xP * STRIDE
                                xPMax = xPMin + args["patchSize"]
                            if yP == no_yPatches - 1:
                                yPMax = imgHeight
                                yPMin = yPMax - args["patchSize"]
                            else:
                                yPMin = yP * STRIDE
                                yPMax = yPMin + args["patchSize"]

                            no_Patches += 1
                            bboxPatch = (xPMin, yPMin, xPMax, yPMax)
                            imgPatch = cvImg[yPMin:yPMax, xPMin:xPMax, :]

                            if '.jpg' in imgName:
                                fnamePatch = os.path.join(OUTPUT_IMGS_PATH, imgName.replace('.jpg', '_'+str(no_Patches)+'.jpg'))
                            elif '.JPG' in imgName:
                                fnamePatch = os.path.join(OUTPUT_IMGS_PATH, imgName.replace('.JPG', '_'+str(no_Patches)+'.jpg'))
                            fnameCSV_l = fnamePatch.split('/')[2:]
                            fnameCSV = '/'.join(fnameCSV_l)

                            # annotations for the patch
                            annPatch = []
                            
                            # get annotations inside the patch
                            for region in imgAnn['regions']: # loop over every annotation in the image
                                x = region['shape_attributes']['x']
                                y = region['shape_attributes']['y']
                                width = region['shape_attributes']['width']
                                height = region['shape_attributes']['height']
                                _classIdx = get_class_idx(classesDict, className=region['region_attributes']['clase'])
                                # Omit invalid classes
                                if _classIdx is None:
                                    continue
                                _class = classesDict[_classIdx]['id']

                                xMin, yMin, xMax, yMax = x, y, x+width, y+height
                                xMin, yMin, xMax, yMax, _class = int(xMin), int(yMin), int(xMax), int(yMax), int(_class)

                                bbox = (xMin, yMin, xMax, yMax)
                                if check_obj_in_patch(bbox, bboxPatch):
                                    newBBox = (bbox[0]-bboxPatch[0], bbox[1]-bboxPatch[1], bbox[2]-bboxPatch[0], bbox[3]-bboxPatch[1])
                                    #print('newBBox: {}'.format(newBBox))
                                    # truncate any bounding box coordinates that fall outside
                                    xMin = min(max(0, int(newBBox[0])), args["patchSize"])
                                    yMin = min(max(0, int(newBBox[1])), args["patchSize"])
                                    xMax = min(max(0, int(newBBox[2])), args["patchSize"])
                                    yMax = min(max(0, int(newBBox[3])), args["patchSize"])
                                    newBBox = (xMin, yMin, xMax, yMax)

                                    #imgAnnPath = os.path.join(args['datasetVersionDir'].split('/')[-1], os.path.basename(fnamePatch))
                                    item = [fnamePatch] + list(newBBox) + [_class]
                                    annPatch.append(item)

                                    # count classes
                                    classesDict[_classIdx]['count'] = classesDict[_classIdx]['count'] + 1

                            # Write the annotations in the image to CSV file
                            if dType == 'train':
                                save = False
                                if len(annPatch) > 0:
                                    no_trainExamples += len(annPatch)
                                    save = True
                                else:# empty image
                                    if args["keepEmpty"]:
                                        print('keeping empty image: {}'.format(args["keepEmpty"]))
                                        item = [fnamePatch] + [None,None,None,None,None]
                                        annPatch.append(item)
                                        save = True
                                if save:
                                    # save patch image
                                    cv2.imwrite(fnamePatch, imgPatch)
                                    no_trainImg += 1
                                    # write to outputCSV
                                    trainWriter.writerows(annPatch)
                            elif dType == 'val':
                                save = False
                                if len(annPatch):
                                    no_valExamples += len(annPatch)
                                    save = True
                                else:# empty image
                                    if args["keepEmpty"]:
                                        item = [fnamePatch] + [None,None,None,None,None]
                                        annPatch.append(item)
                                        save = True
                                if save:
                                    # save patch image
                                    cv2.imwrite(fnamePatch, imgPatch)
                                    no_valImg += 1
                                    # write to outputCSV
                                    valWriter.writerows(annPatch)      
                    # delete downloaded image
                    os.remove(imgLocalPath)
                        
                    #break # uncomment to check code         
        print("[INFO] {} train annotations written...".format(no_trainExamples))
        print("[INFO] {} val annotations written...".format(no_valExamples))
        print("[INFO] total {} annotations".format(no_trainExamples+no_valExamples))

        print("[INFO] {} train images...".format(no_trainImg))
        print("[INFO] {} val images...".format(no_valImg))
        print("[INFO] total {} images".format(no_trainImg+no_valImg))

        detailsPrint = '[INFO] With \n'
        for item in classesDict:
            detailsPrint += '{} {} labels\n'.format(item['count'], item['name'])

        print(detailsPrint)
        '''print('[INFO] With {} techo labels \n \
            {} vehiculo labels \n \
                {} pickup labels \n \
                    {} camion labels \n \
                        {} carga labels \n \
                            {} tractor labels \n \
                                {} maquinaria labels \n \
                                    {} animal labels \n \
                                        {} tuberia labels \n \
                                            {} juegos labels \n \
                                                {} piscina labels \n \
                                                    '.format(no_techo, no_vehiculo, no_pickup, no_camion, no_carga, no_tractor, no_maquinaria, no_animal,\
                                                        no_tuberia, no_juegos, no_piscina))'''

        print("[INFO] csv files completed")
if args["mode"] == 'test':
    # annotation objects
    annTest = []
    # annotations counter
    no_testExamples = 0
    # images counter
    no_images = 0

    # open the output CSV files
    with open(OUTPUT_CSV_TEST, "w") as testCSV:
        testWriter = csv.writer(testCSV)

        # read next annotation file
        with open(INPUT_TEST_FILE, 'r') as dataset:
            print(dataset)
            # load content
            jsonDataset = json.load(dataset)

            # loop over images
            for imgAnnIdx in jsonDataset:
                imgAnn = jsonDataset[imgAnnIdx]
   
                # get annotations inside the patch
                for region in imgAnn['regions']: # loop over every annotation in the image
                    x = region['shape_attributes']['x']
                    y = region['shape_attributes']['y']
                    width = region['shape_attributes']['width']
                    height = region['shape_attributes']['height']
                    _classIdx = get_class_idx(classesDict, className=region['region_attributes']['clase'])
                    # Omit invalid classes
                    if _classIdx is None:
                        continue
                    _class = classesDict[_classIdx]['id']

                    xMin, yMin, xMax, yMax = x, y, x+width, y+height
                    xMin, yMin, xMax, yMax, _class = int(xMin), int(yMin), int(xMax), int(yMax), int(_class)
                    bbox = (xMin, yMin, xMax, yMax)

                    item = [imgAnn['filename']] + list(bbox) + [_class]
                    annTest.append(item)

                    # count classes
                    classesDict[_classIdx]['count'] = classesDict[_classIdx]['count'] + 1
                    no_testExamples += 1
                no_images += 1
        # Write the annotations in the image to CSV file
        testWriter.writerows(annTest)
                           
    print("[INFO] {} test annotations written...".format(no_testExamples))
    print("[INFO] {} test images...".format(no_images))

    detailsPrint = '[INFO] With \n'
    for item in classesDict:
        detailsPrint += '{} {} labels\n'.format(item['count'], item['name'])

    print(detailsPrint)

print("[INFO] csv files completed")

# TODO: 
## 1. Generar automáticamente el archivo de classes.csv para RetinaNet