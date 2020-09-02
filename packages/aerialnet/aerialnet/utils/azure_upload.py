import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob._generated.models._models_py3 import StorageErrorException
from datetime import date
import threading
from aerialnet.utils.classes import label_classname
import json

class AzureClient:
    def __init__(self, connection_string, container_name, model_version):
        service_client = BlobServiceClient.from_connection_string(connection_string)
        self.client = service_client.get_container_client(container_name)
        self.modelVersion = model_version

    def upload_file(self, source, blobDst):
        '''
        Upload a single file to a path inside the container
        '''
        #print(f'Uploading {source} to {blobDst}')
        try:
            with open(source, 'rb') as data:
                self.client.upload_blob(name=blobDst, data=data, overwrite=True)
        except StorageErrorException:
            pass


    def data_formatting(self, imgURL, selected_boxes, selected_labels):
        file_attributes = {"model_version": self.modelVersion}

        jsonRegions = []
        # loop over detections
        for (box, label) in zip(selected_boxes, selected_labels):
            x = int(box[0])
            y = int(box[1])
            xMax = int(box[2])
            yMax = int(box[3])
            width = xMax-x
            height = yMax-y

            labl = int(label)
            class_l = label_classname(labl)
            
            jsonRegions.append({"shape_attributes": {"name": "rect", "x": x, "y": y, "width": width, "height": height},\
                "region_attributes": {"clase": class_l, "map_to_class_id": labl}})
        
        # write image annotations
        jsonObj = {"filename": imgURL, "size": "-1", "regions": jsonRegions, "file_attributes": file_attributes}
        with open('via_ann.json', 'w') as fp:
            json.dump(jsonObj, fp)
        return 'via_ann.json'

    def upload_data(self, imgURL, selected_boxes, selected_labels):
        jsonFile = self.data_formatting(imgURL, selected_boxes, selected_labels)

        currentDate = date.today().strftime("%Y%m%d")
        fname = os.path.basename(imgURL).replace('.jpg', '.json').replace('.JPG', '.json')
        blobDst = os.path.join(currentDate, fname)

        self.upload_file(jsonFile, blobDst)

    def upload_predictions(self, imgURL, selected_boxes, selected_scores, selected_labels):
        #print('Creating upload thread')
        uploadThread = threading.Thread(target=self.upload_data, args=(imgURL, selected_boxes, selected_labels,))
        uploadThread.start()