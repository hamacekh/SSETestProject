# proxy_app.py
import asyncio
from dataclasses import dataclass
from typing import Callable

from fastapi import FastAPI, Request, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
import httpx
import requests
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] %(message)s')
logger = logging.getLogger('proxy_app')


@dataclass
class ResponseStatus:
    finish_reason: str | None = None

# Asynchronous endpoint
@app.get('/stream')
async def proxy_stream(request: Request):
    backend_url = 'http://localhost:8001/stream'  # Backend server URL

    logger.info('Client connected to async proxy endpoint.')

    async def event_generator():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream('GET', backend_url) as resp:
                    async for line in resp.aiter_lines():
                        if await request.is_disconnected():
                            logger.info('Client disconnected from async proxy.')
                            break
                        if line.startswith('data:'):
                            data = line[5:]
                            logger.info(f'Async proxying data: {data}')
                            yield {'data': data}
            except GeneratorExit:
                logger.info('Client disconnected from async proxy.')
                raise
            except asyncio.CancelledError as e:
                logger.info(f'Client cancelled async proxy. {e}')
                raise
            except Exception as exc:
                logger.error(f'Error in async proxy: {exc}')
                raise exc

    return EventSourceResponse(event_generator())


# Synchronous endpoint
@app.get('/sync_stream')
def sync_proxy_stream(request: Request, background_tasks: BackgroundTasks):
    backend_url = 'http://localhost:8001/stream'  # Backend server URL

    logger.info('Client connected to sync proxy endpoint.')

    def cleanup_job(resp: requests.Response, response_status: ResponseStatus) -> Callable[[], None]:
        def cleanup() -> None:
            if response_status.finish_reason is None:
                logger.info("Cleaning up after user disconnect.")
                resp.close()
            else:
                logger.info(f"Request ended because of: {response_status.finish_reason}")
        return cleanup

    def event_generator():
        status = ResponseStatus()
        try:
            with requests.get(backend_url, stream=True) as resp:
                resp.raise_for_status()
                background_tasks.add_task(cleanup_job(resp, status))
                for line in resp.iter_lines():
                    if not line:
                        continue  # Skip empty lines
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        data = decoded_line[5:]
                        logger.info(f'Sync proxying data: {data}')
                        yield {'data': data}
            status.finish_reason = 'Streaming ended correctly'
        except requests.exceptions.RequestException as exc:
            status.finish_reason = 'Server response ended prematurely'
            logger.error(f'Server response ended prematurely: {exc}')
        except Exception as exc:
            status.finish_reason = 'Error in sync proxy'
            logger.error(f'Error in sync proxy: {exc}')
            raise
        except GeneratorExit:
            logger.info('Generator detected exit')
            raise
        finally:
            logger.info('Sync proxy event generator finished.')

    return EventSourceResponse(event_generator())
