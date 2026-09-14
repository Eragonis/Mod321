
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from time import sleep
from air_sensor import AirSensor
from light_sensor import LightSensor
from distance_sensor import DistanceSensor
from sound_player import SoundPlayer
import mimetypes
import json
import os
import textwrap
import RPi.GPIO as GPIO
import smbus




air_sensor = AirSensor()

light_sensor = LightSensor()

distance_sensor = DistanceSensor()

sound_player = SoundPlayer("Mission.mp3")

host = "0.0.0.0"
port = 8080

sleep(1)


class Server(BaseHTTPRequestHandler):
    def sendJSON(self, object: object, code: int = 200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Vary", "Origin")
        self.send_header("Context-type", "text/plain")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(object).encode())

        self.wfile.write(response.encode)




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
        query = parse_qs(parsed.query)


        if self.path == "/":
            self.serveStatic()

        if self.path == "/metrics":
            air = air_sensor.readAir()
            light = light_sensor.readLight()
            response = textwrap.dedent(f"""
            # HELP senor_light measured light intensity in lux\n\
            # TYPE senor_light gazge\n\
            senor_light {light}
            """)

        if self.path == "/api/air":
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
                })

        if self.path == "/api/light":
            self.sendJSON(
                {
                    "status": "ok",
                    "data": {
                        "label": "Illuminance",
                        "value": light_sensor.readLight(),
                        "unit": "lux",
                    },
                }
            )

        if self.path == "/api/distance":
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


        if self.path == "/api/sound/toggle":
            playing = sound_player.toggle()
            self.sendJSON({"status": "ok", "playing": playing})

        if self.path == "/api/sound/restart":
            playing = sound_player.restart()
            self.sendJSON({"status": "ok", "playing": playing})

        if self.path == "/api/sound/seek":
            seconds = query.get("seconds", ["0"])[0]
            try:
                seconds = float(seconds)
                playing = sound_player.seek(seconds)
                self.sendJSON({"status": "ok", "playing": playing, "seconds": seconds})
            except ValueError:
                self.sendJSON({"status": "error", "message": "invalid seconds"}, code=400)

        if self.path == "/api/sound/status":
            self.sendJSON({"status": "ok", "playing": sound_player.status()})



if GPIO.RPI_REVISION == 1:
    bus = smbus.SMBus(0)
else:
    bus = smbus.SMBus(1)


class LightSensor:
    def __init__(self):
        # Definiere Konstante vom Datenblatt

        self.DEVICE = 0x5C  # Standart I2C Geräteadresse

        self.POWER_DOWN = 0x00  # Kein aktiver zustand
        self.POWER_ON = 0x01  # Betriebsbereit
        self.RESET = 0x07  # Reset des Data registers

        # Starte Messungen ab 4 Lux.
        self.CONTINUOUS_LOW_RES_MODE = 0x13
        # Starte Messungen ab 1 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        # Starte Messungen ab 0.5 Lux.
        self.CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        # Starte Messungen ab 1 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        # Starte Messungen ab 0.5 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        # Starte Messungen ab 4 Lux.
        # Nach messung wird Gerät in einen inaktiven Zustand gesetzt.
        self.ONE_TIME_LOW_RES_MODE = 0x23

    def convertToNumber(self, data):
        # Einfache Funktion um 2 Bytes Daten
        # in eine Dezimalzahl umzuwandeln
        return (data[1] + (256 * data[0])) / 1.2

    def readLight(self):
        data = bus.read_i2c_block_data(self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)


def main():
    web_server = HTTPServer((host, port), Server)
    print(f"Server started and listen to {host}:{port}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

print("Server stopped")
 
