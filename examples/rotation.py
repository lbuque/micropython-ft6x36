# SPDX-FileCopyrightText: 2022 lbuque
#
# SPDX-License-Identifier: MIT

from machine import Pin
from machine import I2C
import time
from ft6x36 import FT6x36

# M5Stack Core2
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Lilygo T-Watch 2019 / 2020 V1 / 2020 V2 / 2020 V3
# i2c = I2C(0, scl=Pin(32), sda=Pin(23))

print("I2C Scan:", i2c.scan())
t = FT6x36(i2c, rotation=FT6x36.LANDSCAPE_INVERTED, width=320, height=240)

while True:
    p = t.get_positions()
    p and print(p)
    time.sleep(0.1)
