import asyncio
import machine

UNIT_MS = 200
PAUSE = 2000

WIFI_WAITING = "ti-ta-ti"
WIFI_SERVER_CONNECTED = "ti"
WIFI_CLIENT_CONNECTED = "ti-ti"

status = [1]*10

def Set(str):
    global status
    status = [1 if x == 'ti' else 3 for x in str.split('-')]

led = machine.Pin("LED", machine.Pin.OUT)

async def RunBlink():
    while True:
        i = 0
        while i < len(status):
            led.value(1)
            l = status[i]
            await asyncio.sleep_ms(UNIT_MS*l)
            led.value(0)
            await asyncio.sleep_ms(UNIT_MS)
            i += 1
        await asyncio.sleep_ms(PAUSE)
