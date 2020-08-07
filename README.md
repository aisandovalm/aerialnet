# AERIALNET

## 1. Give execution permision to scripts
```sh
chmod +x scripts/install_aerialnet.sh
chmod +x packages/ml_api/run.sh
chmod +x scripts/run_tfserving.sh
chmod +x scripts/install_nvidia_docker.sh
```

## 2. Install nvidia-docker
```sh
./scripts/install_nvidia_docker.sh
```

## 3. Create environment
```sh
conda env create -f environment.yml
```

## 4. Activate environment
```sh
conda activate aerialnet_env
```

## 5. Install package
```sh
./scripts/install_aerialnet.sh packages/aerialnet/
```

## 6. Check installation
```sh
python
import aerialnet
aerialnet.__version__
```

## 7. Run tfserving
```sh
./scripts/run_tfserving.sh
```

## 8. Run app
```sh
cd packages/ml_api
./run.sh
```

## 9. Test app
```sh
curl -X GET "http://192.168.1.6:5000/health"
```
```sh
curl -X GET "http://192.168.1.6:5000/version"
```
```sh
curl --data "img_url=https://droneimagesstorage.blob.core.windows.net/avionimagefiles/2020-06-01_13-54-40_GPS.jpg" --data "output_img=1" -X POST "http://192.168.1.6:5000/predict"
```
```sh
curl --data "img_url=https://droneimagesstorage.blob.core.windows.net/dronblob/luis.pirela@kauel.com/2020/08/06/DJI_0436.JPG" --data "output_img=1" -X POST "http://192.168.1.6:5000/predict"
```
```sh
curl --data "img_url=https://droneimagesstorage.blob.core.windows.net/dronblob/antoniojosesolano2012@gmail.com/2020/08/06/2020-08-06_13:53:38-3749377-DJI_0334.jpg" -X POST "http://192.168.1.6:5000/predict"
```