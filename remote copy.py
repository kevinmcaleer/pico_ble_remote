# Kevin McAleer
# 2023-06-28
# Bluetooth cores specification versio 5.4 (0x0D)

import struct
import sys

import aioble
import bluetooth
import machine
import uasyncio as asyncio
from micropython import const
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2 as DISPLAY
import jpegdec
import gc
from gui import draw_logo

gc.collect()

display = PicoGraphics(DISPLAY)
WIDTH, HEIGHT = display.get_bounds()
white = display.create_pen(255,255,255)
black = display.create_pen(0,0,0)
blue = display.create_pen(0,0,255)
display.set_pen(white)
display.clear()

text = "BurgerBot Online..."
display.set_pen(blue)
draw_logo(1,1,display)
display.update()
display.set_pen(black)
center = display.measure_text(text, 1, 0)
display.text(text, WIDTH//2 - center, HEIGHT//2)
display.update()
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
alive = False

async def remote_task():
    """ Send the event to the connected device """
    while True and alive:
        if button_a.read():
            print('Button A pressed')
            button_characteristic.write(b"a")   
        elif button_b.read():
            print('Button B pressed')
            button_characteristic.write(b"b")   
        elif button_x.read():
            print('Button X pressed')
            button_characteristic.write(b"x")   
        elif button_y.read():
            print('Button Y pressed')
            button_characteristic.write(b"y")
        else:
            button_characteristic.write(b"!")
        await asyncio.sleep_ms(10)

# Serially wait for connections. Don't advertise while a central is
# connected.    
async def peripheral_task():
    global connected, alive
    while True and alive:
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
            alive = False
            return
    print('robot disconnected')

async def blink_task():
    toggle = True
    while True and alive:
        led.value(toggle)
        toggle = not toggle
        # print(f'blink {toggle}, connected: {connected}')
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)
    led.off()
        
async def main():
    tasks = []
    tasks = [
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(blink_task()),
        asyncio.create_task(remote_task()),
    ]
    await asyncio.gather(*tasks)

while True:
    asyncio.run(main())