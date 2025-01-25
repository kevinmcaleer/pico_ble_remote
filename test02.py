import aioble
import bluetooth
import machine
import uasyncio as asyncio
from burgerbot import Burgerbot

_REMOTE_UUID = bluetooth.UUID(0x1848)
_ENV_SENSE_UUID = bluetooth.UUID(0x1848) 
_REMOTE_CHARACTERISTICS_UUID = bluetooth.UUID(0x2A6E)

LED_PIN = "LED"
BLINK_CONNECTED = 1000
BLINK_DISCONNECTED = 250

led = machine.Pin(LED_PIN, machine.Pin.OUT)
connected = False
alive = False

bot = Burgerbot()
bot.stop()

async def find_remote():
    """Scans for the Bluetooth remote control device."""
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == "KevsRobots":
                print("Found KevsRobots")
                if _ENV_SENSE_UUID in result.services():
                    print("Found Robot Remote Service")
                    return result.device
    return None

async def blink_task():
    """Blinks the LED on and off depending on the connection status."""
    print('Blink task started')
    while alive:
        led.value(not led.value())
        await asyncio.sleep_ms(BLINK_CONNECTED if connected else BLINK_DISCONNECTED)
    print('Blink task stopped')

def move_robot(command):
    """Moves the robot based on the received command."""
    if command == b'a':
        bot.forward(0.1)
    elif command == b'b':
        bot.backward(0.1)
    elif command == b'x':
        bot.turnleft(0.1)
    elif command == b'y':
        bot.turnright(0.1)
    bot.stop()

async def peripheral_task():
    """Manages the Bluetooth connection and handles robot control."""
    global connected, alive
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
        print("Connected")
        alive = True
        connected = True

        try:
            robot_service = await connection.service(_REMOTE_UUID)
            if robot_service is None:
                raise RuntimeError("Robot service not found")
            
            control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)
            if control_characteristic is None:
                raise RuntimeError("Control characteristic not found")
            
            await control_characteristic.subscribe(notify=True)
            while connected:
                command = await control_characteristic.notified()
                move_robot(command)
        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            connected = False
            alive = False
            print("Disconnected")
    
async def main():
    """Main function to start the tasks."""
    await asyncio.gather(blink_task(), peripheral_task())

asyncio.run(main())
