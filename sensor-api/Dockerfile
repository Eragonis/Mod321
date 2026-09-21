FROM python:3.12

RUN pip install RPi.GPIO dht11 smbus paho-mqtt
RUN pip install smbus
#RUN apt-get update && apt-get install -y libasound2-dev alsa-utils && rm -rf /var/lib/apt/lists/*
#RUN pip install pygame
RUN apt-get update && apt-get install -y libasound2-dev alsa-utils ffmpeg && rm -rf /var/lib/apt/lists/*


WORKDIR /usr/src/app
