import asyncio
import machine
import wifistream
import jobs
import timestats

MODE = wifistream.Mode.SERVER
comm = wifistream.WifiStream(MODE)

SERVER = wifistream.Mode.SERVER

led = machine.Pin("LED", machine.Pin.OUT)

async def blinkTask():
    while True:
        led.toggle()
        time = 1000 if comm.connected else 100
        if MODE != SERVER:
            time *= 2
        await asyncio.sleep_ms(1000 if comm.connected else 100)

async def commTask():
    await comm.connectAndStartJobs()
    count = 0
    lastMsg = ""
    while True:
        msg = comm.recv()
        while msg is not None:
            print("received:", msg)
            lastMsg = msg
            msg = comm.recv()
        comm.send(f"hi {count} | " + lastMsg[:20])
        count += 1
        await asyncio.sleep_ms(500 if MODE == SERVER else 1000)

async def main():
    jobs.start(blinkTask())
    jobs.start(commTask())
    jobs.start(timestats.stats.run())
    await jobs.STOP.wait()


if __name__ == '__main__':
    jobs.runMain(main())
