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
connected = False
alive = False

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
    print('blink task started')
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        blink = 1000
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)

async def peripheral_task():
    print('starting peripheral task')
    global connected
    connected = False
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
        print(f"Connected: {connection}")
        connected = True
        alive = True
        while True and alive:
            try:
                robot_service = await connection.service(_REMOTE_UUID)
                print(f"robot_service {robot_service}")
                control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)
                print(f"control_characteristic {control_characteristic}")
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                return
            
            while True:
                if control_characteristic == None:
                    print('no characteristic')
                    await asyncio.sleep_ms(10)
                    return
                
                if control_characteristic != None:
#                     print("checking for button presses")
                    try:
                        command = await control_characteristic.read()
                        if command != b'!':
                            print(f"command was {command}")

                        if command == b'a':
                            print("a button pressed")
                        elif command == b'b':
                            print("b button pressed")
                        elif command == b'x':
                            print("x button pressed")
                        elif command == b'y':
                            print("y button pressed")
                        await asyncio.sleep_ms(1)
                        
                    except TypeError:
                        print(f'something went wrong; remote disconnected?')
                        connected = False
                        alive = False
                        return
                    except asyncio.TimeoutError:
                        print(f'something went wrong; timeout error?')
                        connected = False
                        alive = False
                        return
                    except asyncio.GattError:
                        print(f'something went wrong; Gatt error - did the remote die?')
                        connected = False
                        alive = False
                        return
                await asyncio.sleep_ms(1)
                

async def main():
    tasks = []
    tasks = [
        asyncio.create_task(blink_task()),
        asyncio.create_task(peripheral_task()),
    ]
    await asyncio.gather(*tasks)
    
while True:
    asyncio.run(main())