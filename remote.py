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
from pimoroni import Button
# from btzero import _BUTTON, _encode_message

def uid():
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())

MANUFACTURER_ID = const(0x02A29)
MODEL_NUMBER_ID = const(0x2A24)
SERIAL_NUMBER_ID = const(0x2A25)
HARDWARE_REVISION_ID = const(0x2A26)
BLE_VERSION_ID = const(0x2A28)

EVENT_BUTTON_A = const(0x01)
EVENT_BUTTON_B = const(0x02)
EVENT_BUTTON_X = const(0x03)
EVENT_BUTTON_Y = const(0x04)

buttons = []

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

buttons.append(button_a)
buttons.append(button_b)
buttons.append(button_x)
buttons.append(button_y)

led = machine.Pin("LED", machine.Pin.OUT)

DEVICE_INFO_UUID = bluetooth.UUID(0x180A)
SERVICE_UUID = bluetooth.UUID(0x1815)
BUTTON_UUID = bluetooth.UUID(0x0000)

#_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# advertising frequency
_ADV_INTERVAL_MS = 250_000

device_info = aioble.Service(DEVICE_INFO_UUID)

# Manufacturer Name String
aioble.Characteristic(device_info, bluetooth.UUID(MANUFACTURER_ID), read=True, initial="KevsRobots")

# Model Number String
aioble.Characteristic(device_info, bluetooth.UUID(MODEL_NUMBER_ID), read=True, initial="1.0")

# Serial Number String
aioble.Characteristic(device_info, bluetooth.UUID(SERIAL_NUMBER_ID), read=True, initial=uid())

# Hardware Revision String
aioble.Characteristic(device_info, bluetooth.UUID(HARDWARE_REVISION_ID), read=True, initial=sys.version)

# Remote BLE version
aioble.Characteristic(device_info, bluetooth.UUID(BLE_VERSION_ID), read=True, initial="1.0")

remote_service = aioble.Service(SERVICE_UUID)

button_characteristic = aioble.Characteristic(remote_service, BUTTON_UUID, read=True, notify=True)

# Register the remote control service
aioble.register_services(remote_service, device_info)

def _encode_message(character:str):
    """ Encode a message to send to the remote device """
    return struct.pack("<h", ord(character))



async def send_data(event):
    """ Send the event to the connected device """
    if event == EVENT_BUTTON_A:
        button_characteristic.write(b"left")
        button_characteristic.notify(b'optional data')
        await button_characteristic.indicate(timeout_ms=2000)
    if event == EVENT_BUTTON_B:
        button_characteristic.write(b"right")
        button_characteristic.notify(_encode_message("!"))
        await button_characteristic.indicate(timeout_ms=2000)
    if event == EVENT_BUTTON_X:
        button_characteristic.write(b"up")
        button_characteristic.notify(b'optional data')
        await button_characteristic.indicate(timeout_ms=2000)
    if event == EVENT_BUTTON_Y:
        button_characteristic.write(_encode_message("d"))
        
        # button_characteristic.write(b"down")
        # button_characteristic.notify(b'optional data')
        # await button_characteristic.indicate(timeout_ms=2000)
        button_characteristic.notify()
#         await button_characteristic.indicate(timeout_ms=2000)

# Check status of buttons
async def check_buttons():
    last_reading = time.ticks_ms()
    while True:
        if button_a.read():
            print('Button A pressed')
            await send_data(EVENT_BUTTON_A)

        if button_b.read():
            print('Button B pressed')
            await send_data(EVENT_BUTTON_B)
        if button_x.read():
            print('Button X pressed')
            await send_data(EVENT_BUTTON_X)
        if button_y.read():
            print('Button Y pressed')
            await send_data(EVENT_BUTTON_Y)

        await asyncio.sleep_ms(100)

async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(_ADV_INTERVAL_MS, name="KevsRobots", appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL, services=[SERVICE_UUID]) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()

        except asyncio.CancelledError:
            print('disconnected!')

async def blink_task():
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        print(f'blink {toggle}')
        await asyncio.sleep_ms(1000)
        
async def main():
    tasks = [
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(blink_task()),
        asyncio.create_task(check_buttons()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())