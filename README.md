# AERIALNET

# Give execution permision to scripts
chmod +x scripts/install_aerialnet.sh
chmod +x packages/ml_api/run.sh
chmod +x scripts/run_tfserving.sh
chmod +x scripts/install_nvidia_docker.sh

# Install nvidia-docker
./scripts/install_nvidia_docker.sh

# Create environment
conda env create -f environment.yml

# Activate environment
conda activate aerialnet_env

# Install package
./scripts/install_aerialnet.sh packages/aerialnet/

# Check installation
python
import aerialnet
aerialnet.__version__

# Run tfserving
./scripts/run_tfserving.sh

# Run app
cd packages/ml_api
./run.sh

# Test app
curl -X GET "http://192.168.1.6:5000/health"

curl -X GET "http://192.168.1.6:5000/version"

curl --data "img_url=https://droneimagesstorage.blob.core.windows.net/avionimagefiles/2020-06-01_13-54-40_GPS.jpg" --data "output_img=1" -X POST "http://192.168.1.6:5000/predict"