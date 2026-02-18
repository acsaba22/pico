import time
import asyncio

REPORTFREQUENCY = 2

def formatUs(us):
    if us < 1e3:
        return f"{us} us"
    if us < 1e6:
        return f"{us/1e3:.2f} ms"
    return f"{us/1e6:.2f} s"

class Timer:
    def __init__(self, name, parent = None):
        self.name = name
        self.count = 0
        self.totalTime = 0
        self.lastStarted = -1
        self.parent = parent
        global stats
        stats.register(self)

    def start(self):
        if self.lastStarted != -1:
            raise ValueError("Timer already started")
        self.lastStarted = time.ticks_us()
    
    def __enter__(self):
        if self.lastStarted != -1:
            raise ValueError("Timer already started")
        self.lastStarted = time.ticks_us()
        return self

    def stop(self):
        now = time.ticks_us()
        currentRun = time.ticks_diff(now, self.lastStarted)
        self.totalTime += currentRun
        self.count += 1
        self.lastStarted = -1

    def __exit__(self, *args):
        now = time.ticks_us()
        currentRun = time.ticks_diff(now, self.lastStarted)
        self.totalTime += currentRun
        self.count += 1
        self.lastStarted = -1

    def reportStr(self, programTime):
        s = self.name # TODO .ljust(10)
        percentStr = ""
        if self.parent == None:
            percentStr = f"{self.totalTime / programTime * 100:.1f}% [Total]"
        else:
            percentStr = f"{self.totalTime / self.parent.totalTime * 100:.1f}% [{self.parent.name}]"
        ret = f"{s} - {percentStr} {formatUs(self.totalTime)} / {self.count} = {formatUs(self.totalTime // max(1, self.count))}"
        return ret



class Stats:
    def __init__(self):
        self.timers = []
        self.startupTime = time.ticks_ms()
    
    def register(self, timer):
        self.timers.append(timer)
    
    def _totalTime(self):
        now = time.ticks_ms()
        return 1000 * time.ticks_diff(now, self.startupTime)

    def report(self):
        with reportTimer:
            totalTime = self._totalTime()
            print("# Total Time: " + formatUs(totalTime))
            for t in self.timers:
                print("#", t.reportStr(totalTime))

    async def run(self):
        while True:
            await asyncio.sleep(REPORTFREQUENCY)
            self.report()

stats = Stats()
reportTimer = Timer("Stats.report")
