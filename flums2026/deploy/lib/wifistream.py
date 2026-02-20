import network
import asyncio
import jobs
from collections import deque
import plog
import blinkstatus

QUEUE_SIZE = 100

SSID = "pico-test3"
PASSWORD = "12345678"
PORT = 1234
SERVER_IP = "192.168.4.1" # don't touch, should be ap.ifconfig()[0]

class Mode:
    SERVER = 0
    CLIENT = 1
    AUTO = 2

AUTO_TIMEOUT_MS = 5000


class WifiServer:
    def __init__(self):
        blinkstatus.Set(blinkstatus.WIFI_WAITING)
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        ap.active(True)
        ap.config(ssid=SSID, password=PASSWORD)
        plog.info(f"Wifi server start: {SSID} ; Server IP: {ap.ifconfig()[0]}"  )
        self._connected = asyncio.Event()
        self._reader = None
        self._writer = None

    async def _handleClient(self, reader, writer):
        ip, port = writer.get_extra_info('peername')
        plog.info("connected:", ip, port)
        self._reader = reader
        self._writer = writer
        self._connected.set()

    async def waitForClient(self):
        plog.info("Waiting for connection")
        server = await asyncio.start_server(self._handleClient, "0.0.0.0", PORT)
        await self._connected.wait()
        blinkstatus.Set(blinkstatus.WIFI_SERVER_CONNECTED)
        return self._reader, self._writer


class WifiClient:
    def __init__(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        plog.info(f"Wifi Client Connecting: {SSID}")
        self._wlan = wlan

    def shutdown(self):
        self._wlan.active(False)

    async def connect(self, timeout_ms=None):
        plog.info(f"Waiting to connect")
        elapsed = 0
        while not self._wlan.isconnected():
            if timeout_ms is not None and elapsed >= timeout_ms:
                return False, None, None
            await asyncio.sleep_ms(100)
            elapsed += 100
        plog.info("Client IP:", self._wlan.ifconfig()[0])
        try:
            reader, writer = await asyncio.open_connection(SERVER_IP, PORT)
            plog.info("connected to server")
            blinkstatus.Set(blinkstatus.WIFI_CLIENT_CONNECTED)
            return True, reader, writer
        except OSError:
            return False, None, None

class Stream:
    def __init__(self):
        self._sendQueue = deque((), QUEUE_SIZE)
        self._sendEvent = asyncio.Event()
        self._receiveQueue = deque((), QUEUE_SIZE)
        self._receiveEvent = asyncio.Event()

    def _startJobs(self, reader, writer):
        jobs.start(self._senderTask(writer))
        jobs.start(self._receiverTask(reader))

    async def _senderTask(self, writer):
        while True:
            await self._sendEvent.wait()
            self._sendEvent.clear()
            while self._sendQueue:
                msg = self._sendQueue.popleft()
                plog.deb("# COMM_SEND: ", msg)
                writer.write((msg + "\n").encode())
                await writer.drain()

    async def _receiverTask(self, reader):
        while True:
            data = await reader.readline()
            plog.deb("# COMM_RECIEVED: ", data.decode().strip())
            if data == b"":
                self._receiveQueue.append(None)  # disconnected
                break
            if len(self._receiveQueue) >= QUEUE_SIZE:
                plog.info("WARNING: receiveQueue full, dropping message")
            else:
                self._receiveQueue.append(data.decode().strip())
                self._receiveEvent.set()

    def send(self, msg):
        if len(self._sendQueue) >= QUEUE_SIZE:
            plog.info("WARNING: sendQueue full, dropping message")
        else:
            self._sendQueue.append(msg)
            self._sendEvent.set()

    def receive(self):
        if not self._receiveQueue:
            return None
        return self._receiveQueue.popleft()

    async def receiveBlocking(self):
        while not self._receiveQueue:
            self._receiveEvent.clear()
            await self._receiveEvent.wait()
        return self._receiveQueue.popleft()


class WifiStream(Stream):
    def __init__(self, mode = Mode.AUTO):
        super().__init__()
        self.mode = mode
        self.connected_ = False
        if mode == Mode.SERVER:
            self._server = WifiServer()
        elif mode == Mode.CLIENT:
            self._client = WifiClient()
        elif mode == Mode.AUTO:
            self._client = WifiClient()
        else:
            raise ValueError(f"bad mode {mode}")

    def isConnected(self):
        return self.connected_

    async def connectAndStartJobs(self):
        jobs.start(blinkstatus.RunBlink())
        if self.mode == Mode.AUTO:
            ok, reader, writer = await self._client.connect(timeout_ms=AUTO_TIMEOUT_MS)
            if ok:
                plog.info("AUTO: acting as client")
            else:
                plog.info("AUTO: no server found, acting as server")
                self._client.shutdown()
                self._server = WifiServer()
                reader, writer = await self._server.waitForClient()
        elif self.mode == Mode.SERVER:
            reader, writer = await self._server.waitForClient()
        else:
            _, reader, writer = await self._client.connect()
        self.connected_ = True
        self._startJobs(reader, writer)
