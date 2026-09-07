import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BOARD)

class DistanceSensor():
    TRIG = 36  # BOARD-Pin für Trigger
    ECHO = 32  # BOARD-Pin für Echo

    def __init__(self):
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, False)
        time.sleep(0.5)  # Sensor braucht kurz Ruhe zum Initialisieren
        self.result = self.readDistance()
        threading.Thread(target=self.update, daemon=True).start()

    def readDistance(self):
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        timeout = time.time() + 0.04  # ~40ms Sicherheitslimit
        pulse_start = time.time()
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return None

        pulse_end = time.time()
        timeout = time.time() + 0.04
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return None

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)

    def update(self):
        while True:
            value = self.readDistance()
            if value is not None:
                self.result = value
            time.sleep(0.5)

    def readDistanceValue(self):
        return self.result
