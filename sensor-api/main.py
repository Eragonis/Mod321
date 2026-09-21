from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from time import sleep
from air_sensor import AirSensor
from light_sensor import LightSensor
from distance_sensor import DistanceSensor
from sound_player import SoundPlayer
import threading
import mimetypes
import json
import os

import paho.mqtt.client as mqtt

air_sensor = AirSensor()
light_sensor = LightSensor()
distance_sensor = DistanceSensor()
sound_player = SoundPlayer("Mission.ogg")

host = "0.0.0.0"
port = 8080


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Brocker with result {reason_code}")

def on_message(client, userdata, msg:object):
    print(msg.topic + " " + str(msg.payload))

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("172.17.0.1",1883 ,60)


sleep(1)


class Server(BaseHTTPRequestHandler):
    def sendJSON(self, object: object, code: int = 200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Vary", "Origin")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(object).encode())

    def serveStatic(self):
        local_file_path = os.path.join(".", self.path[1:], "index.html")
        print(local_file_path)

        if os.path.exists(local_file_path) and os.path.isfile(local_file_path):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Vary", "Origin")

            mime_type, _ = mimetypes.guess_type(local_file_path)
            if mime_type:
                self.send_header("Content-type", mime_type)
            else:
                self.send_header("Content-type", "application/octet-stream")

            self.end_headers()

            with open(local_file_path, "rb") as file:
                self.wfile.write(file.read())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.serveStatic()

        if path == "/api/air":
            air = air_sensor.readAir()
            self.sendJSON(
                {
                    "status": "ok",
                    "data": [
                        {
                            "label": "Temperature",
                            "value": air.temperature,
                            "unit": "°C",
                        },
                        {"label": "Humidity", "value": air.humidity, "unit": "%"},
                    ],
                }
            )

        if path == "/api/light":
            self.sendJSON(
                {
                    "status": "ok",
                    "data": {
                        "label": "Illuminance",
                        "value": light_sensor.readLightValue(),
                        "unit": "lux",
                    },
                }
            )

        if path == "/api/distance":
            self.sendJSON(
                {
                    "status": "ok",
                    "data": {
                        "label": "Distance",
                        "value": distance_sensor.readDistanceValue(),
                        "unit": "cm",
                    },
                }
            )

        if path == "/api/sound/toggle":
            playing = sound_player.toggle()
            self.sendJSON({"status": "ok", "playing": playing})

        if path == "/api/sound/restart":
            playing = sound_player.restart()
            self.sendJSON({"status": "ok", "playing": playing})

        if path == "/api/sound/seek":
            seconds = query.get("seconds", ["0"])[0]
            try:
                seconds = float(seconds)
                playing = sound_player.seek(seconds)
                self.sendJSON({"status": "ok", "playing": playing, "seconds": seconds})
            except Exception as e:
                print(f"Seek error: {e}")
                self.sendJSON({"status": "error", "message": str(e)}, code=400)

        if path == "/api/sound/status":
            self.sendJSON({"status": "ok", "playing": sound_player.status()})

def read_distance_sencor(delay):
    while True:
        distance = distance_sensor.readDistance()
        mqtt_client.publish("Eragonis/sensors/disatance", distance, qos=2) #qos qualiti of service
        print(distance)
        sleep(delay)

def main():
    web_server = ThreadingHTTPServer((host, port), Server)
    print(f"Server started and listen to {host}:{port}")

    distanceSebsorThred = threading.Thread(
        target=read_distance_sencor , args=(0.3,), daemon=True
)
    distanceSebsorThred.start()

    try:
        mqtt_client.loop_start()
        mqtt_client.publish("Eragonis/up", "true", qos=2)
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

print("Server stopped")
