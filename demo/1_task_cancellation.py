import asyncio
import threading


def tprint(message):
    print(f"[{threading.get_ident()}]: {message}")


async def worker():
    try:
        tprint("Worker started")
        for i in range(5):
            await asyncio.sleep(1)
            tprint(f"Worker completed iteration {i}")
        tprint("Worker completed")
    except asyncio.CancelledError:
        tprint("Worker was cancelled")
        raise


async def main():
    task = asyncio.create_task(worker())
    tprint("Main keeps running")
    await asyncio.sleep(3.1)  # Allow the worker to run for a bit
    tprint("Cancelling the worker task")
    task.cancel()  # Initiate cancellation
    await asyncio.sleep(4)
    tprint("Main app stops")



asyncio.run(main())
