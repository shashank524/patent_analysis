# Use the Nvidia Pytorch Image if you want to train locally
# Start FROM Nvidia PyTorch image https://ngc.nvidia.com/catalog/containers/nvidia:pytorch

# FROM nvcr.io/nvidia/pytorch:21.05-py3

# Starting from python image

FROM python:3.7
# Install linux packages
RUN apt update && apt install -y zip htop screen libgl1-mesa-glx
RUN apt update && apt install -y build-essential libpoppler-cpp-dev pkg-config python3-dev poppler-utils
# RUN apt-get update && apt-get install -y python3-opencv ca-certificates python3-dev git wget sudo ninja-build

# Install python dependencies
COPY requirements.txt .
# COPY new_requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --user tensorboard cmake   # cmake from apt-get is too old
RUN pip uninstall -y nvidia-tensorboard nvidia-tensorboard-plugin-dlprof
RUN pip install -r requirements.txt coremltools onnx gsutil notebook

WORKDIR /app

#COPY best.pt /usr/src/app/best.pt

# Set environment variables
ENV HOME=/app

# Checking if all files are included
RUN ls

# Installing Detectron2 Dependencies
RUN pip install --user torch==1.9 torchvision==0.10 -f https://download.pytorch.org/whl/cu111/torch_stable.html
RUN pip install --user 'git+https://github.com/facebookresearch/fvcore'
RUN pip install cython pyyaml==5.1
RUN pip install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'


# Copy contents
COPY . /app


EXPOSE 8501

#RUN cat .dockerignore
ENTRYPOINT ["streamlit", "run"]

CMD ["app.py"]
# ---------------------------------------------------  Extras Below  ---------------------------------------------------

# Build and Push
# t=ultralytics/yolov5:latest && sudo docker build -t $t . && sudo docker push $t
# for v in {300..303}; do t=ultralytics/coco:v$v && sudo docker build -t $t . && sudo docker push $t; done

# Pull and Run
# t=ultralytics/yolov5:latest && sudo docker pull $t && sudo docker run -it --ipc=host --gpus all $t

# Pull and Run with local directory access
# t=ultralytics/yolov5:latest && sudo docker pull $t && sudo docker run -it --ipc=host --gpus all -v "$(pwd)"/coco:/usr/src/coco $t

# Kill all
# sudo docker kill $(sudo docker ps -q)

# Kill all image-based
# sudo docker kill $(sudo docker ps -qa --filter ancestor=ultralytics/yolov5:latest)

# Bash into running container
# sudo docker exec -it 5a9b5863d93d bash

# Bash into stopped container
# id=$(sudo docker ps -qa) && sudo docker start $id && sudo docker exec -it $id bash

# Send weights to GCP
# python -c "from utils.general import *; strip_optimizer('runs/train/exp0_*/weights/best.pt', 'tmp.pt')" && gsutil cp tmp.pt gs://*.pt

# Clean up
# docker system prune -a --volumes
