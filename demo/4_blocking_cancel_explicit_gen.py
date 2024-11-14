import asyncio
import gc
import threading

import anyio
from starlette.concurrency import iterate_in_threadpool


def tprint(message):
    print(f"[{threading.get_ident()}]: {message}")


def blocking_iterator():
    return BlockingIterator()


class BlockingIterator:
    def __init__(self):
        self.i = 0
        self.closed = False
        self._finalized = False
        tprint("Blocking iterator started")

    def __iter__(self):
        return self

    def __next__(self):
        if self.closed:
            raise StopIteration

        try:
            if self.i < 10:
                tprint(f"Blocking iterator yielding {self.i}")
                import time
                time.sleep(1)  # Simulate blocking work
                value = self.i
                self.i += 1
                return value
            else:
                self._finalize()
                raise StopIteration
        except Exception as exc:
            tprint(f"Blocking iterator caught exception: {exc}")
            self._finalize()
            raise

    def close(self):
        if not self.closed and not self._finalized:
            self.closed = True
            tprint("Blocking iterator detected exit")
            self._finalize()

    def _finalize(self):
        if not self._finalized:
            tprint("Blocking iterator finished")
            self._finalized = True

    def __del__(self):
        tprint("Blocking iterator garbage collected")
        self.close()


async def async_task():
    tprint("Async task started")
    iterator = blocking_iterator()
    try:
        async for value in iterate_in_threadpool(iterator):
            tprint(f"Received value {value} in async task")
    except asyncio.CancelledError:
        tprint("Async task was cancelled")
        asyncio.create_task(anyio.to_thread.run_sync(iterator.close))
        raise  # Propagate cancellation


async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(async_task)
        await asyncio.sleep(3)  # Let the task run for a bit
        tprint("Cancelling the async task")
        tg.cancel_scope.cancel()  # Cancel the task

    tprint("The app keeps running")
    await asyncio.sleep(1)
    tprint("Requesting gc")
    gc.collect()
    await asyncio.sleep(1) # wait for a bit so gc has a chance to complete
    tprint("The app stops")


asyncio.run(main())
