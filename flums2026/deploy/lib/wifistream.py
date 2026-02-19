import network
import asyncio
import jobs
from collections import deque

QUEUE_SIZE = 100

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
        self._wlan = wlan

    async def connect(self):
        while not self._wlan.isconnected():
            await asyncio.sleep_ms(100)
        print("Client IP:", self._wlan.ifconfig()[0])
        reader, writer = await asyncio.open_connection(SERVER_IP, PORT)
        print("connected to server")
        return reader, writer


class Stream:
    def __init__(self):
        self._sendQueue = deque((), QUEUE_SIZE)
        self._sendEvent = asyncio.Event()
        self._receiveQueue = deque((), QUEUE_SIZE)

    def _startJobs(self, reader, writer):
        jobs.start(self._senderTask(writer))
        jobs.start(self._receiverTask(reader))

    async def _senderTask(self, writer):
        while True:
            await self._sendEvent.wait()
            self._sendEvent.clear()
            while self._sendQueue:
                msg = self._sendQueue.popleft()
                writer.write((msg + "\n").encode())
                await writer.drain()

    async def _receiverTask(self, reader):
        while True:
            data = await reader.readline()
            if data == b"":
                self._receiveQueue.append(None)  # disconnected
                break
            if len(self._receiveQueue) >= QUEUE_SIZE:
                print("WARNING: receiveQueue full, dropping message")
            else:
                self._receiveQueue.append(data.decode().strip())

    def send(self, msg):
        if len(self._sendQueue) >= QUEUE_SIZE:
            print("WARNING: sendQueue full, dropping message")
        else:
            self._sendQueue.append(msg)
            self._sendEvent.set()

    def receive(self):
        if not self._receiveQueue:
            return None
        return self._receiveQueue.popleft()


class WifiStream(Stream):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.connected = False
        if mode == Mode.SERVER:
            self._server = WifiServer()
        elif mode == Mode.CLIENT:
            self._client = WifiClient()
        else:
            raise ValueError(f"bad mode {mode}")

    async def connectAndStartJobs(self):
        if self.mode == Mode.SERVER:
            reader, writer = await self._server.waitForClient()
        else:
            reader, writer = await self._client.connect()
        self.connected = True
        self._startJobs(reader, writer)
