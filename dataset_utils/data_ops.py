import os, sys
import json
import argparse
import io

CLASSES_MAP = ['Techo', 'Vehículo', 'Pickup', 'Camión', 'Carga/Container', 'Tractor', 'Maquinaria', 'Animal', 'Tuberia/Escombros', 'Juegos/Plaza', 'Piscina/Estanque']

def filter_classes(file, dataVersion, justMaq=True, outputDir=None):
    with open(file, 'r') as f:
        jsonDict = json.load(f)

    for idx, imgObj in enumerate(jsonDict):
        newRegions = []
        haveMaq = False
        for region in imgObj['regions']:
            className = region['region_attributes']['clase']
            newRegions.append(region)
            if className == 'Maquinaria':
                haveMaq = True

        jsonDict[idx]['regions'] = newRegions

        # Delete image if there is not Maquinaria
        if justMaq and not haveMaq:
            print('Deleting image at idx {}'.format(idx))
            jsonDict.pop(idx)
            
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

def add_source_dataset_from_VIA(inputFile, fromDate, sourceDirPath='../datasets/source_dataset'):
    '''
        Extract annotations from a VIA file, filter out the images without Maquinaria and generate a new VIA file.
        The VIA file generated is saved in outputDir inside fromDate folder.
    '''
    outputDirPath = os.path.join(sourceDirPath, fromDate)
    os.makedirs(outputDirPath, exist_ok=True)
    outputVIAFile = os.path.join(outputDirPath, 'viaJsonFile.json')

    with open(inputFile, 'r') as f:
        jsonDict = json.load(f)

    newDict = []
    for idx, viaId in enumerate(jsonDict):
        imgObj = jsonDict[viaId]
        haveMaq = False
        for region in imgObj['regions']:
            className = region['region_attributes']['clase']
            # if image has Maquinaria, save it and continue with the next image
            if className == 'Maquinaria':
                haveMaq = True
                break

        # Delete image if there is not Maquinaria
        if haveMaq:
            newDict.append(imgObj)

    print('Writing {} images in {}'.format(len(newDict), outputVIAFile))
    with io.open(outputVIAFile, 'w', encoding='utf8') as f:
        json.dump(newDict, f, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", help="Operation to run", required=True)
    parser.add_argument("--dataVersion", help="Version of the output data", required=False)
    parser.add_argument("--filePath", help="Path to input file (JSON format)", required=False)
    parser.add_argument("--outputDir", help="Path to the output dir", required=False)
    parser.add_argument("--justMaq", help="Keeping image only if it has Maquinaria class", required=False, default=False)
    parser.add_argument("--inputFile", help="Path to the VIA file", required=False)
    parser.add_argument("--fromDate", help="VIA file corresponding date", required=False)
    parser.add_argument("--sourceDirPath", help="Path to the source dataset dir", required=False, default='../datasets/source_dataset')
    args = parser.parse_args()

    if args.op == 'FILTER_CLASSES':
        filter_classes(args.filePath, args.dataVersion, justMaq=args.justMaq, outputDir=args.outputDir)
    if args.op == 'FORMAT_SONACOL_AS_VIA':
        format_sonacol_as_via(args.filePath, args.dataVersion, justMaq=args.justMaq, outputDir=args.outputDir)
    if args.op == 'ADD_SOURCE_DATASET':
        add_source_dataset_from_VIA(args.inputFile, args.fromDate, sourceDirPath=args.sourceDirPath)