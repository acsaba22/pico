import asyncio
import sys

# use STOP.set() to stop the program
# use await STOP.wait() to guard the finishing of the main program.
# start your main with asyncio.
STOP = asyncio.Event()

async def guarded(coro):
    try:
        await coro
    except Exception as e:
        sys.print_exception(e)
        STOP.set()

# use to start jobs (not the main): startJob(f())
def start(f):
    asyncio.create_task(guarded(f))

# use with runMain(main())
def runMain(m):
    asyncio.run(m)
