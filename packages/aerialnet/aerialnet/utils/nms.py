def get_iou(boxObjA, boxObjB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxObjA[0], boxObjB[0])
    yA = max(boxObjA[1], boxObjB[1])
    xB = min(boxObjA[2], boxObjB[2])
    yB = min(boxObjA[3], boxObjB[3])
    '''# check if boxObjB is inside boxObjA
    if (boxObjB == [xA, yA, xB, yB]).all():
        # boxB is inside boxA
        return 1'''
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxObjA[2] - boxObjA[0] + 1) * (boxObjA[3] - boxObjA[1] + 1)
    boxBArea = (boxObjB[2] - boxObjB[0] + 1) * (boxObjB[3] - boxObjB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou

def non_max_suppression_all_classes(boxes, scores, labels, iou_threshold=0.5):
    """ Retorna solo las marcas que tienen la maxima probabilidad dentro de un radio, y no comparten una IntersectionOverUnion mayor a IOU """
    excluded_indices = []
    for i in range(0,len(boxes)):
        obj1_box, _, obj1_label = boxes[i], scores[i], labels[i]
        for j in range(i+1,len(boxes)):
            obj2_box, _, obj2_label = boxes[j], scores[j], labels[j]
            if (get_iou(obj1_box, obj2_box) > iou_threshold):
                #print('excluding idx={}, class={}, score={}, bbox={}'.format(j, obj2_label, obj2_score, obj2_box))
                excluded_indices.append(j)
    
    excluded_indices = list(set(excluded_indices)) #Elimina indices repetidos
    included_indices = [idx for idx in range(len(boxes)) if idx not in excluded_indices]
    #print(included_indices)
    return included_indices