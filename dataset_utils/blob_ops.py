import os, sys
import json
from azure.storage.blob import ContainerClient
import argparse


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", help="Operation to run")
    parser.add_argument("--dateDir", help="Name of date folder where the blobs to download are")
    parser.add_argument("--outputDir", help="Path to the output dir")
    args = parser.parse_args()

    if args.op == 'DOWNLOAD_BLOBS_AS_ONE_JSON':
        outputDirFull = os.path.join(args.outputDir, args.dateDir)
        if not os.path.exists(outputDirFull):
            os.makedirs(outputDirFull, exist_ok=True)

        download_blobs_as_one_json(args.dateDir, outputDirFull)