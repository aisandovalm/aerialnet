import os, sys
import json
import argparse
import io

CLASSES_MAP = ['Techo', 'Vehículo', 'Pickup', 'Camión', 'Carga/Container', 'Tractor', 'Maquinaria', 'Animal', 'Tuberia/Escombros', 'Juegos/Plaza', 'Piscina/Estanque']

def filter_classes(file, dataVersion, justMaq=True, outputDir=None):
    # Read classes
    CLASSES_FILE = os.path.join('../datasets/data', dataVersion, 'CLASSES')
    if not os.path.exists(CLASSES_FILE):
        print('File with info of classes: {} not found, create that file and try again'.format(CLASSES_FILE))
        return

    classesName = []
    file_attributes = ''
    with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            classNum, className = line.split(',')
            className = className.replace('\n', '')
            classesName.append(className)
            file_attributes += '{},{} '.format(classNum, className)

    print('Keeping the following classes: {}'.format(classesName))

    with open(file, 'r') as f:
        jsonDict = json.load(f)

    for idx, imgObj in enumerate(jsonDict):
        newRegions = []
        haveMaq = False
        for region in imgObj['regions']:
            className = region['region_attributes']['clase']
            classIdx = classesName.index(className)
            if className in classesName:
                print('Keeping region with class: {}'.format(className))
                if className == 'Pickup':
                    region['region_attributes']['map_to_class_id'] = 1
                    region['region_attributes']['clase'] = 'Vehículo'
                newRegions.append(region)
                if className == 'Maquinaria':
                    haveMaq = True
            else:
                print('Deleting class {}'.format(className))

        jsonDict[idx]['regions'] = newRegions

        # Delete image if there is not Maquinaria
        if justMaq and not haveMaq:
            print('Deleting image at idx {}'.format(idx))
            jsonDict[idx] = []

    if outputDir is None:
        outputDir = os.path.dirname(file)
    with io.open(os.path.join(outputDir, 'viaJsonFile.json'), 'w', encoding='utf8') as f:
        json.dump(jsonDict, f, ensure_ascii=False)

def format_sonacol_as_via(file, dataVersion, justMaq=True, outputDir=None):
    print('Formatting SONACOL JSON file as VIA format, with data version: {}'.format(dataVersion))
    
    # Read classes
    CLASSES_FILE = os.path.join('../datasets/data', dataVersion, 'CLASSES')
    if not os.path.exists(CLASSES_FILE):
        print('File with info of classes: {} not found, create that file and try again'.format(CLASSES_FILE))
        return

    classesName = []
    file_attributes = ''
    with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            classNum, className = line.split(',')
            className = className.replace('\n', '')
            classesName.append(className)
            file_attributes += '{},{} '.format(classNum, className)

    with open (file, 'r', encoding='utf-8') as f:
        jsonDict = json.load(f)

    viaJson = []

    for idx, imgObj in enumerate(jsonDict['data']['alerts']['data']):
        imgDict = {'filename': imgObj['url_image'], 'regions':[], 'file_attributes': file_attributes, 'size': "-1"}
        imgRegions = []
        haveMaq = False
        for mark in imgObj['marks']:
            region = {}
            className = mark['category']
            if className == 'Pickup': # Set Pickup as Vehicle
                className = 'Vehículo'
            classIdx = classesName.index(className)
            if classIdx > -1:
                print('Keeping mark with class: {}'.format(className))
                if className == 'Maquinaria':
                    haveMaq = True

                # extract data
                cx = mark['cx']
                cy = mark['cy']
                dx = mark['dx']
                dy = mark['dy']

                x = cx
                y = dy
                width = dx-cx
                height = cy-dy

                imgRegions.append({"shape_attributes": {"name": "rect", "x": x, "y": y, "width": width, "height": height},\
                "region_attributes": {"clase": className, "map_to_class_id": classIdx}})
            else:
                print('Class {} not found'.format(className))

        imgDict['regions'] = imgRegions

        # Not add image if it has not Maquinaria
        if justMaq and not haveMaq:
            print('Omitting image at idx {}: {}'.format(idx, imgObj['url_image']))
        else:
            viaJson.append(imgDict)

    if outputDir is None:
        outputDir = os.path.dirname(file)
    with io.open(os.path.join(outputDir, 'viaJsonFile.json'), 'w', encoding='utf8') as f:
        json.dump(viaJson, f, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", help="Operation to run", required=True)
    parser.add_argument("--dataVersion", help="Version of the output data", required=True)
    parser.add_argument("--filePath", help="Path to input file (JSON format)", required=True)
    parser.add_argument("--outputDir", help="Path to the output dir", required=False)
    parser.add_argument("--justMaq", help="Keeping image only if it has Maquinaria class", required=False, default=False)
    args = parser.parse_args()

    if args.op == 'FILTER_CLASSES':
        filter_classes(args.filePath, args.dataVersion, justMaq=args.justMaq, outputDir=args.outputDir)
    if args.op == 'FORMAT_SONACOL_AS_VIA':
        format_sonacol_as_via(args.filePath, args.dataVersion, justMaq=args.justMaq, outputDir=args.outputDir)