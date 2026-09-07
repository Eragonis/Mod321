FROM python:3.12

RUN pip install RPi.GPIO dht11
RUN pip install smbus
RUN apt-get update && apt-get install -y libasound2-dev alsa-utils && rm -rf /var/lib/apt/lists/*
RUN pip install pygame



WORKDIR /usr/src/app
