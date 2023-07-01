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

_GENERIC = bluetooth.UUID(0x1848)
_BUTTON_UUID = bluetooth.UUID(0x2A6E)
_ROBOT = bluetooth.UUID(0x180A)
                              
_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

ADV_INTERVAL_MS = 250_000

device_info = aioble.Service(_ROBOT)
                              
connection = None

# Create Characteristic for device info
aioble.Characteristic(device_info, bluetooth.UUID(MANUFACTURER_ID), read=True, initial="KevsRobots.com")
aioble.Characteristic(device_info, bluetooth.UUID(MODEL_NUMBER_ID), read=True, initial="1.0")
aioble.Characteristic(device_info, bluetooth.UUID(SERIAL_NUMBER_ID), read=True, initial=uid())
aioble.Characteristic(device_info, bluetooth.UUID(HARDWARE_REVISION_ID), read=True, initial=sys.version)
aioble.Characteristic(device_info, bluetooth.UUID(BLE_VERSION_ID), read=True, initial="1.0")

remote_service = aioble.Service(_GENERIC)

button_characteristic = aioble.Characteristic(
    remote_service, _BUTTON_UUID, notify=True, read=True
)

print("Registering services")

aioble.register_services(remote_service, device_info)

connected = False

async def remote_task():
    """ Task to handle remote control """

    while True:
        if not connected:
            print("Not Connected")
            await asyncio.sleep_ms(1000)
            continue
        if button_a.read():
            print(f"Button A pressed, connection is: {connection}")
            button_characteristic.write(b"a")
            button_characteristic.notify(connection, b"a")
        elif button_b.read():
            print(f"Button B pressed, connection is: {connection}")
            button_characteristic.write(b"b")
            button_characteristic.notify(connection, b"b")
        elif button_x.read():
            print(f"Button X pressed, connection is: {connection}")
            button_characteristic.write(b"x")
            button_characteristic.notify(connection, b"x")
        elif button_y.read():
            print(f"Button Y pressed, connection is: {connection}")
            button_characteristic.write(b"y")
            button_characteristic.notify(connection, b"y")
        else:
            button_characteristic.write(b"!")
            button_characteristic.notify(connection, b"!")
        await asyncio.sleep_ms(10)

async def peripheral_task():
    """ Task to handle peripheral """
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            ADV_INTERVAL_MS,
            name="KevsRobots",
            appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL,
            services=[_GENERIC]
        ) as connection:
            print("Connection from, ", connection.device)
            connected = True
            print("connected {connected}")
            await connection.disconnected()
            print("disconnected")

async def blink_task():
    """ Task to blink LED """
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
        asyncio.create_task(remote_task()),
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(blink_task()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())