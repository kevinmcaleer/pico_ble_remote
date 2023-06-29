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


SERVICE_UUID = bluetooth.UUID(0x1815)
BUTTON_UUID = bluetooth.UUID(0x0000)

def _decode_message(message:bytes):
    """ Decode a message received from the remote device """
    return struct.unpack("<h", message)[0]

async def scan():
    async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print(result, result.name(), result.rssi, result.services())
            if result.name() == None:
                continue
            print (f"result.name: {result.name()}")
            # if result.name() == 'KevsRobots' and SERVICE_UUID in result.services():
            if result.name() == 'KevsRobots':
                print("KevsRobot Bluetooth device found")
                if SERVICE_UUID in result.services():
                    print("KevsRobot Bluetooth device found, scanning for services")
                
                
#                     await asyncio.sleep_ms(250)
                    return result.device
            
    print("no robot found")
    return None

async def main():
    device = await scan()
    await asyncio.sleep_ms(1000)
    if not device:
        print(f"no robot found: {device}")
        return
    
    try:
        print("connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
    
    async with connection:
        try:
            remote_service = await connection.service(SERVICE_UUID)
            print("service", remote_service.uuid)
            
            remote_characteristic = await remote_service.characteristic(BUTTON_UUID)
            print(f"remote characteristic", remote_characteristic.uuid)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            message = _decode_message(await remote_characteristic.read())
            print(f"message: {message}")
            await asyncio.sleep_ms(1000)
        
asyncio.run(main())
