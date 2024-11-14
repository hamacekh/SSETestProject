# backend_server.py

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import logging
import os

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('backend_server')

# Read 'SSE_BACKEND_STOP_AT' from environment variable, default to None
STOP_AT_ENV = os.getenv('SSE_BACKEND_STOP_AT')
if STOP_AT_ENV is None:
    stop_at = None
else:
    try:
        stop_at = int(STOP_AT_ENV)
        if not (1 <= stop_at <= 9):
            logger.warning(f"'SSE_BACKEND_STOP_AT' value {stop_at} is out of expected range (1-9). Ignoring.")
            stop_at = None
    except ValueError:
        logger.error(f"Invalid 'SSE_BACKEND_STOP_AT' value: {STOP_AT_ENV}. It should be an integer between 1 and 9.")
        stop_at = None

# Read 'SSE_BACKEND_HARD_ERROR_AT' from environment variable, default to None
HARD_ERROR_AT_ENV = os.getenv('SSE_BACKEND_HARD_ERROR_AT')
if HARD_ERROR_AT_ENV is None:
    hard_error_at = None
else:
    try:
        hard_error_at = int(HARD_ERROR_AT_ENV)
        if not (1 <= hard_error_at <= 9):
            logger.warning(f"'SSE_BACKEND_HARD_ERROR_AT' value {hard_error_at} is out of expected range (1-9). Ignoring.")
            hard_error_at = None
    except ValueError:
        logger.error(f"Invalid 'SSE_BACKEND_HARD_ERROR_AT' value: {HARD_ERROR_AT_ENV}. It should be an integer between 1 and 9.")
        hard_error_at = None

@app.get('/stream')
async def backend_stream(request: Request):
    logger.info('Client connected to backend stream.')

    async def event_generator():
        for i in range(1, 10):
            # Check if we need to simulate a hard server error
            if hard_error_at and i == hard_error_at:
                logger.info(f'Simulating hard server error at event {i}. Raising exception to abruptly terminate connection.')
                raise ConnectionAbortedError(f"Simulated hard server error at event {i}.")

            # Check if we should stop gracefully
            if stop_at and i == stop_at:
                logger.info(f'Simulating server error at event {i}. Ending stream prematurely gracefully.')
                break  # Simulate server error by ending the stream prematurely

            # Check if client has disconnected
            if await request.is_disconnected():
                logger.info('Client disconnected from backend stream.')
                break

            await asyncio.sleep(1)  # Simulate delay between events
            data = f'Event {i}'
            logger.info(f'Sending data: {data}')
            yield {'data': data}
        else:
            logger.info('Completed sending all events.')

    return EventSourceResponse(event_generator())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend_server:app', host='0.0.0.0', port=8001, reload=True)
