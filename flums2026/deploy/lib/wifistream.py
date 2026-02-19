import network
import asyncio
import jobs

SSID = "pico-test"
PASSWORD = "12345678"
PORT = 1234
SERVER_IP = "192.168.4.1" # don't touch, should be ap.ifconfig()[0]

class Mode:
    SERVER = 0
    CLIENT = 1


class WifiServer:
    def __init__(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(ssid=SSID, password=PASSWORD)
        print("Server IP:", ap.ifconfig()[0])
        self._connected = asyncio.Event()
        self._reader = None
        self._writer = None

    async def _handleClient(self, reader, writer):
        ip, port = writer.get_extra_info('peername')
        print("connected:", ip, port)
        self._reader = reader
        self._writer = writer
        self._connected.set()

    async def waitForClient(self):
        server = await asyncio.start_server(self._handleClient, "0.0.0.0", PORT)
        await self._connected.wait()
        return self._reader, self._writer


class WifiClient:
    def __init__(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
        print("Client IP:", wlan.ifconfig()[0])

    async def connect(self):
        reader, writer = await asyncio.open_connection(SERVER_IP, PORT)
        print("connected to server:")
        return reader, writer


class Stream:
    def __init__(self):
        self._sendList = []
        self._sendEvent = asyncio.Event()
        self._recvList = []

    def _startJobs(self, reader, writer):
        jobs.start(self._senderTask(writer))
        jobs.start(self._receiverTask(reader))

    async def _senderTask(self, writer):
        while True:
            await self._sendEvent.wait()
            self._sendEvent.clear()
            while self._sendList:
                msg = self._sendList.pop(0)
                writer.write((msg + "\n").encode())
                await writer.drain()

    async def _receiverTask(self, reader):
        while True:
            data = await reader.readline()
            if data == b"":
                self._recvList.append(None)  # disconnected
                break
            self._recvList.append(data.decode().strip())

    def send(self, msg):
        self._sendList.append(msg)
        self._sendEvent.set()

    def recv(self):
        if not self._recvList:
            return None
        return self._recvList.pop(0)


class WifiStream(Stream):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        if mode == Mode.SERVER:
            self._server = WifiServer()
        elif mode == Mode.CLIENT:
            self._client = WifiClient()
        else:
            raise ValueError(f"bad mode {mode}")

    async def connectAndStartJobs(self):
        if self.mode == Mode.SERVER:
            reader, writer = await self._server.waitForClient()
            self._startJobs(reader, writer)
        else:
            reader, writer = await self._client.connect()
            self._startJobs(reader, writer)
