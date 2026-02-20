import network
import asyncio
import jobs
import timestats
from timestats import NewTimer


# master
def wifiAccesPoint(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(ssid=ssid, password=password)
    print("Server IP:", ap.ifconfig()[0])  # usually 192.168.4.1


def wifiConnect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("Client IP:", wlan.ifconfig()[0])


async def handleClient(reader, writer):
    ip, port = writer.get_extra_info('peername')
    print("connected:", ip, port)

    data = ""
    # b"" means it disconnected
    while data != b"" or data != b"quit\n":
        data = await reader.readline()
        print("received:", data)
        writer.write(b"ping " + data)
        await writer.drain()
    writer.close()
    print("disconnected:", ip)

async def serverTask():
    server = await asyncio.start_server(handleClient, "0.0.0.0", 1234)
    await server.wait_closed()

async def clientTask():
    print("await open_connection")
    reader, writer = await asyncio.open_connection("192.168.4.1", 1234)
    print("connected")
    count = 0
    while True:
        msg = f"hello {count}\n"
        print("Going to write: " + msg.strip())
        writer.write(msg.encode())
        print("await write " + msg.strip())
        await writer.drain()
        print("await read")
        response = await reader.readline()
        print("got:", response)
        count += 1
        await asyncio.sleep(1)

# SERVER/CLIENT
# MODE = "SERVER"
MODE = "CLIENT"

async def main():
    if MODE == "SERVER":
        wifiAccesPoint("pico-test", "12345678")
        jobs.start(serverTask())
    else:
        wifiConnect("pico-test", "12345678")
        jobs.start(clientTask())
    jobs.start(timestats.stats.run())
    await jobs.STOP.wait()


if __name__ == '__main__':
    jobs.runMain(main())

