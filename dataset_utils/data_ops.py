import os, sys
import json
import argparse
import io

CLASSES_MAP = ['Techo', 'Vehículo', 'Pickup', 'Camión', 'Carga/Container', 'Tractor', 'Maquinaria', 'Animal', 'Tuberia/Escombros', 'Juegos/Plaza', 'Piscina/Estanque']

def filter_classes(file, classes, justMaq=True):
    print('Keeping the following classes: {}'.format(classes))
    
    classesIdx = [CLASSES_MAP.index(_class) for _class in classes]

    with open (file, 'r') as f:
        jsonDict = json.load(f)

    for idx, imgObj in enumerate(jsonDict):
        newRegions = []
        haveMaq = False
        for region in imgObj['regions']:
            objClass = region['region_attributes']['map_to_class_id']
            if objClass in classesIdx:
                print('Keeping region with class: {}'.format(CLASSES_MAP[objClass]))
                if CLASSES_MAP[objClass] == 'Pickup':
                    region['region_attributes']['map_to_class_id'] = 1
                    region['region_attributes']['clase'] = 'Vehículo'
                newRegions.append(region)
                if CLASSES_MAP[objClass] == 'Maquinaria':
                    haveMaq = True
            else:
                print('Deleting class {}'.format(CLASSES_MAP[objClass]))

        jsonDict[idx]['regions'] = newRegions

        # Delete image if there is not Maquinaria
        if justMaq and not haveMaq:
            print('Deleting image at idx {}'.format(idx))
            jsonDict[idx] = []


    outputDir = os.path.dirname(file)
    classesJoin = '_'.join(classes).replace('/', '')
    with io.open(os.path.join(outputDir, 'viaJsonFile_{}.json'.format(classesJoin)), 'w', encoding='utf8') as f:
        json.dump(jsonDict, f, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", help="Operation to run", required=True)
    parser.add_argument("--filePath", help="Path to input file (JSON format)", required=True)
    parser.add_argument("--classes", help="List of classes to keep", nargs='+', required=True)
    args = parser.parse_args()

    if args.op == 'FILTER_CLASSES':
        filter_classes(args.filePath, args.classes)