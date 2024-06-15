# FT6X36 (FT6236/FT6336/FT6436L/FT6436)

This is a micropython module for self-capacitive touch panel controllers produced by FocalTech Systems.

## Feature

- Support rotation
- Support two-point touch

## Install

open a MicroPython REPL and execute these commands inside the REPL

```python
import machine
import network
import time
import mip
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('SSID', 'PASSWORD')
time.sleep(1)
print('Device connected to network: {}'.format(station.isconnected()))
# latest
mip.install("github:lbuque/micropython-ft6x36/ft6x36/ft6x36.py", target="lib")
# or mpy
mip.install("ft6x36", index="https://lbuque.github.io/micropython-ft6x36/mip/0.2.0")
print('Installation completed')
machine.soft_reset()
```

## Thank

Part of the code is from [FT6336U-](https://github.com/vae-V/FT6336U-.git).
