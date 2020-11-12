#!/usr/bin/env bash
 
BASE_DIR=$(pwd)
#PARENT_DIR="$(dirname "$BASE_DIR")"

#echo $BASE_DIR
sudo docker run --gpus all -p 8500:8500 -p 8501:8501 --mount type=bind,source=$BASE_DIR/saved_models,target=/models/aerialnet/5 -e MODEL_NAME=aerialnet -t tensorflow/serving:latest-gpu