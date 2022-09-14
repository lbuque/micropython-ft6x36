from machine import Pin
from machine import I2C
import time
from ft6x36 import FT6x36

if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(32), sda=Pin(23))
    print(i2c.scan())
    t = FT6x36(i2c)
    while True:
        print(t.get_positions())
        time.sleep(0.1)
