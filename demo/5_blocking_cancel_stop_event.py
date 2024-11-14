# The following code originates from starlette.concurrency library
import asyncio
import threading

from starlette.concurrency import iterate_in_threadpool


# Cooperative cancellation example starts here
def blocking_iterator(stop_event):
    print("Blocking iterator started")
    try:
        for i in range(10):
            if stop_event.is_set():
                print("Blocking iterator detected cancellation")
                break
            print(f"Blocking iterator yielding {i}")
            import time
            time.sleep(1)  # Simulate blocking work
            yield i
    finally:
        print("Blocking iterator finished")

async def async_task():
    stop_event = threading.Event()
    try:
        print("Async task started")
        async for value in iterate_in_threadpool(blocking_iterator(stop_event)):
            print(f"Received value {value} in async task")
    except asyncio.CancelledError:
        print("Async task was cancelled")
        stop_event.set()  # Signal the blocking iterator to stop
        # Consume the rest of the iterator to allow it to clean up
        async for _ in iterate_in_threadpool(blocking_iterator(stop_event)):
            pass
        raise  # Propagate cancellation

async def main():
    task = asyncio.create_task(async_task())
    await asyncio.sleep(3.1)  # Let the task run for a bit
    print("Cancelling the async task")
    task.cancel()  # Cancel the task
    try:
        await task
    except asyncio.CancelledError:
        print("Main function caught task cancellation")

asyncio.run(main())
