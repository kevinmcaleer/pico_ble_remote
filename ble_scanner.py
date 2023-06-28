# Kevin McAleer
# 2023-06-28
# Bluetooth cores specification versio 5.4 (0x0D)
# Bluetooth scanner

import sys
import time
import struct
import machine

import uasyncio as asyncio
import aioble
import bluetooth
from micropython import const

async def scan():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print (f"result.name: {result.name()}")
            if result.name() == 'KevsRobots':
                return result.device
    return None

async def main():
    device = await scan()
    if not device:
        print("no robot found")
    
    try:
        print("connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
    
    async with connection:
        while True:
            print('connected')
            await asyncio.sleep_ms(1000)
        
    

asyncio.run(main())