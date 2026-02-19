import asyncio
import machine

led = machine.Pin("LED", machine.Pin.OUT)

UNIT_MS = 100
PAUSE = 1000

class BlinkStatus:
    def __init__(self):
        pass

    async def run(self):
        while True:
            led.value(1)
            await asyncio.sleep_ms(UNIT_MS)
            led.value(0)
            await asyncio.sleep_ms(PAUSE)
