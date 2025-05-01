import time
import board
import busio
import adafruit_scd30


class AdafruitSCD30:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.scd = adafruit_scd30.SCD30(i2c)
        time.sleep(2)

    def read(self):
        if self.scd.data_available:
            co2 = self.scd.CO2
            temperature = self.scd.temperature
            humidity = self.scd.relative_humidity
            return co2, temperature, humidity
        else:
            return None