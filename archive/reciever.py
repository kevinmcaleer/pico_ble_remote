# Kevin McAleer
# 2023-06-28
# Bluetooth cores specification versio 5.4 (0x0D)

import sys
import time
import struct
import machine

import uasyncio as asyncio
import aioble
import bluetooth
from micropython import const

