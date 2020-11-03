import os, sys
import json
from azure.storage.blob import ContainerClient
import argparse
import requests


def download_blobs_as_one_json(dateDir, outputDir):
    # generate json
    viaDict = []
    try:
        with open('../packages/aerialnet/aerialnet/data/AZURE_STORAGE') as version_file:
            AZURE_STORAGE_CONNECTION_STRING = version_file.read()
            CONTAINER_NAME = "aihistory"
        
        container = ContainerClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, container_name=CONTAINER_NAME)

        blob_list = container.list_blobs(name_starts_with=dateDir+'/')

        for idx, blob in enumerate(blob_list):
            print('Downloading blob #{}: {}\n'.format(idx+1, blob.name), flush=True)

            if '.json' in blob.name:
                blob_client = container.get_blob_client(blob.name)
                download_stream = blob_client.download_blob()
                jsonContent = json.loads(download_stream.readall())
                viaDict.append(jsonContent)

        print('Total blobs downloaded: {}'.format(idx+1))
        with open(os.path.join(outputDir, 'viaJsonFile_ORIGINAL.json'), 'w') as f:
            json.dump(viaDict, f)
    except Exception as ex:
        print('Exception:')
        print(ex)

def download_blobs_as_one_json_from_list(inputFile, outputFile):
    # generate json
    viaDict = []
    blobList = []
    with open(inputFile) as listBlobsFile:
        blobList = listBlobsFile.readlines()

    for idx, blob_tuple in enumerate(blobList):
        dateDir, imgName = blob_tuple.split(',')
        imgName = os.path.basename(imgName)
        url = 'https://droneimagesstorage.blob.core.windows.net/aihistory/' + dateDir + '/' + imgName.replace('.jpg', '.json').replace('.JPG', '.json')
        #https://droneimagesstorage.blob.core.windows.net/aihistory/20200901/2020-09-01_08:26:18-3695986-DJI_0038.json
        print('Downloading blob #{}: {}\n'.format(idx+1, url))

        if '.json' in url:
            print('inside json')
            r = requests.get(url)
            if r.status_code == 200:
                jsonContent = r.json()
                viaDict.append(jsonContent)
            elif r.status_code == 400:
                print('400: blob not found')
            else:
                print('blob not found')

    print('Total blobs downloaded: {}'.format(idx+1))
    with open(outputFile, 'w') as f:
        json.dump(viaDict, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", help="Operation to run")
    parser.add_argument("--dateDir", help="Name of date folder where the blobs to download are")
    parser.add_argument("--outputDir", help="Path to the output dir")
    parser.add_argument("--inputFile", help="Path to input file with blob's list")
    parser.add_argument("--outputFile", help="Path to output file with downloaded jsons")
    args = parser.parse_args()

    if args.op == 'DOWNLOAD_BLOBS_AS_ONE_JSON':
        outputDirFull = os.path.join(args.outputDir, args.dateDir)
        if not os.path.exists(outputDirFull):
            os.makedirs(outputDirFull, exist_ok=True)

        download_blobs_as_one_json(args.dateDir, outputDirFull)
    if args.op == 'DOWNLOAD_BLOBS_AS_ONE_JSON_FROM_LIST':
        #os.makedirs(args.outputFile, exist_ok=True)

        download_blobs_as_one_json_from_list(args.inputFile, args.outputFile)