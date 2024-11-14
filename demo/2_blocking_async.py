import asyncio
import threading
import time

import anyio


def tprint(message):
    print(f"[{threading.get_ident()}]: {message}")


def worker():
    # Simulate a blocking I/O operation
    tprint("Worker started")
    try:
        time.sleep(3)
    finally:
        tprint("Worker completed")


async def main():
    tprint("Starting run_sync operation...")
    task = asyncio.create_task(anyio.to_thread.run_sync(worker))
    tprint("Main keeps running")
    await asyncio.sleep(10)
    tprint("Main app stops")


anyio.run(main)
