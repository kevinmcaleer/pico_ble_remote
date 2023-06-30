# June 2023
# Bluetooth cores specification versio 5.4 (0x0D)
# Bluetooth Remote Control
# Kevin McAleer
# KevsRobot.com

import aioble
import bluetooth
import machine
import uasyncio as asyncio

# Bluetooth UUIDS can be found online at https://www.bluetooth.com/specifications/gatt/services/

_REMOTE_UUID = bluetooth.UUID(0x1848)
_ENV_SENSE_UUID = bluetooth.UUID(0x1800) 
_REMOTE_CHARACTERISTICS_UUID = bluetooth.UUID(0x2A6E)

led = machine.Pin("LED", machine.Pin.OUT)

async def find_remote():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:

            # See if it matches our name
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
    
    device = await find_remote()
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
        while True:
            try:
                robot_service = await connection.service(_REMOTE_UUID)
                print(robot_service)
                control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)
                print(control_characteristic)
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                return
            while True:
                if control_characteristic != None:
                    try:
                        temp_deg_c = await control_characteristic.read()
                        print(f"Command: {temp_deg_c}")
                    except TypeError:
                        print(f'something went wrong; remote disconnected?')
                        return
                    except asyncio.TimeoutError:
                        print(f'something went wrong; timeout error?')
                        return
                else:
                    print('no characteristic')
                await asyncio.sleep_ms(1000)
while True:
    asyncio.run(main())