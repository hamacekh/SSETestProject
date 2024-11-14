# The following code originates from starlette.concurrency library
import asyncio
import gc
import threading
import time

import anyio
from starlette.concurrency import iterate_in_threadpool


def tprint(message):
    print(f"[{threading.get_ident()}]: {message}")


def blocking_iterator():
    tprint("Blocking iterator started")
    try:
        for i in range(10):
            tprint(f"Blocking iterator yielding {i}")
            time.sleep(1)  # Simulate blocking work
            yield i
    except GeneratorExit:
        tprint("Blocking iterator detected exit")
    finally:
        tprint("Blocking iterator finished")


async def async_task():
    try:
        tprint("Async task started")
        async for value in iterate_in_threadpool(blocking_iterator()):
            tprint(f"Received value {value} in async task")
    except asyncio.CancelledError:
        tprint("Async task was cancelled")
        # Since we cannot signal the blocking iterator, it will continue running
        raise  # Propagate cancellation


async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(async_task)
        await asyncio.sleep(3)  # Let the task run for a bit
        tprint("Cancelling the async task")
        tg.cancel_scope.cancel()  # Cancel the task

    tprint("The app keeps running")
    await asyncio.sleep(20)
    tprint("The app stops")


asyncio.run(main())
