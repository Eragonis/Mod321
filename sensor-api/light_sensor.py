import smbus
import time
import threading

class LightSensor():
    DEVICE = 0x5c  # Standard I2C Geräteadresse des BH1750

    POWER_DOWN = 0x00
    POWER_ON = 0x01
    RESET = 0x07
    CONTINUOUS_LOW_RES_MODE = 0x13
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    ONE_TIME_LOW_RES_MODE = 0x23

    def __init__(self):
        self.bus = smbus.SMBus(1)  # Bus 1, aktuelle Raspberry Pi Modelle
        self.result = self.readLight()
        threading.Thread(target=self.update, daemon=True).start()

    def convertToNumber(self, data):
        # 2 Bytes Rohdaten in Lux-Wert umwandeln
        return ((data[1] + (256 * data[0])) / 1.2)

    def readLight(self):
        data = self.bus.read_i2c_block_data(self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)

    def update(self):
        while True:
            try:
                self.result = self.readLight()
            except Exception as e:
                print(f"Light sensor read error: {e}")
            time.sleep(0.5)

    def readLightValue(self):
        return self.result
