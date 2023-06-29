import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
import machine
import random
import struct

# org.bluetooth.service.environmental_sensing
_REMOTE_UUID = bluetooth.UUID(0x1848)
_ENV_SENSE_UUID = bluetooth.UUID(0x1800) 
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
#_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x1800)

led = machine.Pin("LED", machine.Pin.OUT)

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100


async def find_temp_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
#             if not result.name() == None: print(result.name())
            # See if it matches our name and the environmental sensing service.
            if result.name() == "KevsRobots":
                print("Found KevsRobots")
                for item in result.services():
                    print (item)
                if _ENV_SENSE_UUID in result.services():
                    print("Found Robot Remote Service")
                    return result.device
            
    return None

async def blink_task():
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        print(f'blink {toggle}')
        await asyncio.sleep_ms(1000)

async def main():
    
    device = await find_temp_sensor()
    if not device:
        print("Robot Remote not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
        
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
        
    async with connection:
        print("Connected")
        try:
            temp_service = await connection.service(_REMOTE_UUID)
            print(temp_service)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
            print(temp_characteristic)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return
        while True:
            if temp_characteristic != None:
                temp_deg_c = await temp_characteristic.read()
                print(f"Command: {temp_deg_c}")
            else:
                print('no characteristic')
            await asyncio.sleep_ms(1000)

asyncio.run(main())