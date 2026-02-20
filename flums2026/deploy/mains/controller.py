import asyncio
from machine import Pin
import plog
import wifistream
import jobs

plog.setLevel(plog.DEBUG)

comm = wifistream.WifiStream(wifistream.Mode.CLIENT)

async def controller():
    names = ["u", "d", "r", "l", "A", "B"]

    button_up = Pin(14, Pin.IN, Pin.PULL_UP)
    button_down = Pin(13, Pin.IN, Pin.PULL_UP)
    button_right = Pin(12, Pin.IN, Pin.PULL_UP)
    button_left = Pin(11, Pin.IN, Pin.PULL_UP)
    button_A = Pin(10, Pin.IN, Pin.PULL_UP)
    button_B = Pin(9, Pin.IN, Pin.PULL_UP)
    buttons = [button_up, button_down, button_right, button_left, button_A, button_B]

    last = [5]*len(names)

    while True:
        for i in range(len(names)):
            await asyncio.sleep_ms(0)
            newval = buttons[i].value()
            if last[i] != newval:
                last[i]=newval
                if newval==0:
                    msg = names[i]+"-1"
                    comm.send(msg)
                    plog.info(msg)
                else:
                    msg = names[i]+"-0"
                    comm.send(msg)
                    plog.deb(msg)

async def main():
    jobs.start(controller())
    jobs.start(comm.connectAndStartJobs())
    await jobs.STOP.wait()


if __name__ == '__main__':
    jobs.runMain(main())