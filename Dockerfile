FROM nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04

RUN apt -qq -y update \
	&& apt -qq -y upgrade
RUN apt -y install python3.7
RUN apt -y install python3-pip
RUN python3.7 -m pip install --upgrade pip
RUN apt-get install -y libgl1-mesa-glx

RUN which python3.7
RUN which pip3

RUN ln -s /usr/bin/python3.7 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN python --version
RUN which pip

WORKDIR /usr/src/app
COPY . .
RUN pip3 install tensorflow==2.4.0
RUN pip3 install cffi
RUN pip install --no-cache-dir -r requirements.txt
ADD https://github.com/prafair/detect-parking-lot/raw/main/detection_model-ex-017--loss-0022.945.h5 /tmp/new_model.h5
EXPOSE 80
CMD ["python", "main.py"]