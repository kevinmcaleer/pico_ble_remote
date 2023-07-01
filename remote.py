# Kevin McAleer
# 2023-06-28
# Bluetooth cores specification versio 5.4 (0x0D)

import sys

import aioble
import bluetooth
import machine
import uasyncio as asyncio
from micropython import const
from pimoroni import Button

def uid():
    """ Return the unique id of the device as a string """
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())

MANUFACTURER_ID = const(0x02A29)
MODEL_NUMBER_ID = const(0x2A24)
SERIAL_NUMBER_ID = const(0x2A25)
HARDWARE_REVISION_ID = const(0x2A26)
BLE_VERSION_ID = const(0x2A28)

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

led = machine.Pin("LED", machine.Pin.OUT)

_ENV_SENSE_UUID = bluetooth.UUID(0x180A)
_GENERIC = bluetooth.UUID(0x1848)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x1800)
_BUTTON_UUID = bluetooth.UUID(0x2A6E)

_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# Advertising frequency
ADV_INTERVAL_MS = 250_000

device_info = aioble.Service(_ENV_SENSE_UUID)

connection = None

# Create characteristics for device info
aioble.Characteristic(device_info, bluetooth.UUID(MANUFACTURER_ID), read=True, initial="KevsRobotsRemote")
aioble.Characteristic(device_info, bluetooth.UUID(MODEL_NUMBER_ID), read=True, initial="1.0")
aioble.Characteristic(device_info, bluetooth.UUID(SERIAL_NUMBER_ID), read=True, initial=uid())
aioble.Characteristic(device_info, bluetooth.UUID(HARDWARE_REVISION_ID), read=True, initial=sys.version)
aioble.Characteristic(device_info, bluetooth.UUID(BLE_VERSION_ID), read=True, initial="1.0")

remote_service = aioble.Service(_GENERIC)

button_characteristic = aioble.Characteristic(
    remote_service, _BUTTON_UUID, read=True, notify=True
)

print('registering services')
aioble.register_services(remote_service, device_info)

connected = False

async def remote_task():
    """ Send the event to the connected device """

    while True:
        if not connected:
            print('not connected')
            await asyncio.sleep_ms(1000)
            continue
        if button_a.read():
            print(f'Button A pressed, connection is: {connection}')
            button_characteristic.write(b"a")   
            button_characteristic.notify(connection,b"a")
        elif button_b.read():
            print('Button B pressed')
            button_characteristic.write(b"b")
            button_characteristic.notify(connection,b"b")
        elif button_x.read():
            print('Button X pressed')
            button_characteristic.write(b"x")
            button_characteristic.notify(connection,b"x")
        elif button_y.read():
            print('Button Y pressed')
            button_characteristic.write(b"y")
            button_characteristic.notify(connection,b"x")
        else:
            button_characteristic.write(b"!")
        await asyncio.sleep_ms(10)
            
# Serially wait for connections. Don't advertise while a central is
# connected.    
async def peripheral_task():
    print('peripheral task started')
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            ADV_INTERVAL_MS, 
            name="KevsRobots", 
            appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL, 
            services=[_ENV_SENSE_TEMP_UUID]
        ) as connection:
            print("Connection from", connection.device)
            connected = True
            print(f"connected: {connected}")
            await connection.disconnected()
            print(f'disconnected')
        

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
        
async def main():
    tasks = [
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(blink_task()),
        asyncio.create_task(remote_task()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())