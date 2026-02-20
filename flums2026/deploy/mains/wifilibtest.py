import asyncio
import machine
import wifistream
import jobs
import timestats
import blinkstatus

MODE = wifistream.Mode.SERVER
comm = wifistream.WifiStream(MODE)

# led = machine.Pin("LED", machine.Pin.OUT)

# async def blinkTask():
#     while True:
#         led.toggle()
#         await asyncio.sleep_ms(1000 if comm.isConnected() else 100)

async def commTask():
    count = 0
    lastMsg = ""
    while True:
        msg = comm.receive()
        while msg is not None:
            print("received:", msg)
            lastMsg = msg
            msg = comm.receive()
        if comm.isConnected():
            comm.send(f"hi {count} | " + lastMsg[:20])
            count += 1
        await asyncio.sleep_ms(1000)

async def main():
    jobs.start(comm.connectAndStartJobs())
    jobs.start(commTask())
    jobs.start(timestats.stats.run())
    await jobs.STOP.wait()


if __name__ == '__main__':
    jobs.runMain(main())

